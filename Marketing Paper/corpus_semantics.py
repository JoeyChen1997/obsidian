"""Local, evidence-located concept, statement and temporal relation candidates."""

import argparse
from collections import defaultdict, deque
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import time
import unicodedata

import corpus_rag
import paperlist
import semantic_context


DEFAULT_DB = paperlist.DEFAULT_DB.with_name('research-semantics-v2.sqlite3')
VOCABULARY = Path(__file__).with_name('research_concepts.json')
VERSION = '2'
SCHEMA = '''
CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scanned (
 paper INTEGER PRIMARY KEY, stamp TEXT NOT NULL, fingerprint TEXT NOT NULL,
 passages INTEGER NOT NULL, references_checked INTEGER NOT NULL,
 pairs_with_context INTEGER NOT NULL, ambiguous_contexts INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS mentions (
 paper INTEGER NOT NULL, concept TEXT NOT NULL, alias TEXT NOT NULL,
 passage INTEGER NOT NULL, page INTEGER NOT NULL, section TEXT NOT NULL,
 PRIMARY KEY(paper,concept));
CREATE INDEX IF NOT EXISTS mention_concept ON mentions(concept,paper);
CREATE TABLE IF NOT EXISTS statements (
 paper INTEGER NOT NULL, kind TEXT NOT NULL, label TEXT NOT NULL,
 passage INTEGER NOT NULL, page INTEGER NOT NULL, section TEXT NOT NULL,
 excerpt TEXT NOT NULL, PRIMARY KEY(paper,kind,label));
CREATE TABLE IF NOT EXISTS relations (
 earlier INTEGER NOT NULL, later INTEGER NOT NULL, earlier_year INTEGER NOT NULL,
 later_year INTEGER NOT NULL, kind TEXT NOT NULL, passage INTEGER NOT NULL,
 page INTEGER NOT NULL, section TEXT NOT NULL, ref_page INTEGER NOT NULL,
 excerpt TEXT NOT NULL, method TEXT NOT NULL, evidence_pieces TEXT NOT NULL,
 PRIMARY KEY(later,earlier,kind));
CREATE INDEX IF NOT EXISTS relation_forward ON relations(earlier,later);
'''

ALIAS_TOKEN = re.compile(r'[\W_]+')
LINE_HYPHEN = re.compile(r'(?<=\w)[-\u2010]\s+(?=[a-z])')
SENTENCE_END = re.compile(r'(?<!et al)(?<!\be\.g)(?<!\bi\.e)[.!?](?=\s+[A-Z]|$)')
LABEL = re.compile(r'\b(proposition|lemma|corollary|theorem|assumption)\s+([A-Z]?\d+(?:\.\d+)*[a-z]?)'
                   r'(?:[.)](?=\s)|\s*:\s+|\s+\([^()]{4,100}\)[.:](?=\s))', re.I)
ASSUME = re.compile(r'\b(?:we (?:also |further |additionally )?assume (?:that |an? |the |each |all |both )|'
                    r'(?:consumers?|firms?|sellers?|retailers?) (?:are|is) assumed to\b)', re.I)
NOT_DECLARATION = re.compile(r'\b(?:proofs? (?:of|for)|by|see|from|in|of|as in|according to|'
                             r'follows? from|show(?:s|n)? in|recall|stated in)\s*$', re.I)
OWN = r'(?:we|(?:in )?our (?:model|framework|paper|analysis|setting|results?|findings?))'
EXTEND = r'(?:extend(?:s)?|generaliz(?:e|es)|generalis(?:e|es)|modif(?:y|ies)|build(?:s)? on|follow(?:s)?|adopt(?:s)?)'
CHANGE = re.compile(r'(?:our (?:model|framework|setting) (?:allows?|relaxes?|differs?|introduces?|adds?)|'
                    + OWN + r' (?:assume|allow|relax|differ|introduce|add))', re.I)
OUTCOME = r'our (?:results?|findings?|predictions?|conclusions?)'
OWN_ACTION = re.compile(r'\b' + OWN + r'\s+(?:(?:directly|explicitly|closely)\s+)?(' + EXTEND + r')'
                        r'\s+(?:(?:the |a |an )?(?:(?:baseline |theoretical |analytical )?(?:model|framework|analysis|approach|setup|'
                        r'setting|specification|work|results?|assumptions?) (?:of|in|developed by|proposed by) )?)$', re.I)
RESULT_OBJECT = re.compile(r'\b' + OUTCOME + r' (?P<verb>contrast(?:s)?|differ(?:s)?|conflict(?:s)?|are consistent)'
                           r'(?: \w+){0,2} (?:with|from) (?:the )?(?:(?:results?|findings?|predictions?|conclusions?|those) (?:in|of|by|reported in) )?$', re.I)
LIMIT_OBJECT = re.compile(r'\b(?:we (?:show|find|demonstrate) that )?'
                          r'(?:the )?(?:results?|conclusions?|predictions?|findings?) (?:of|in) $', re.I)
LIMIT_TAIL = re.compile(r"^\s*(?:hold(?:s)? only|no longer hold(?:s)?|need(?:s)? not hold|"
                        r"fail(?:s)? to hold|depend(?:s)? (?:on|crucially on)|(?:is|are) (?:specific|special|limited) to)\b", re.I)
CUE = re.compile(r'\b(?:extend|generaliz|generalis|modif|adopt|follow|build|contrast|differ|unlike|'
                 r'consistent|compare|support|replicat|confirm|assum|relax|restrict|hold|depend|limited|'
                 r'special|qualif|endogen|same)\w*', re.I)
YEAR = re.compile(r'\b(?:18|19|20)\d{2}[a-z]?\b', re.I)
OTHER_CITATION = re.compile(r'\b[A-Z][A-Za-z-]{2,}(?:\s+et al\.)?\s*,?\s*\(?\s*(?:18|19|20)\d{2}[a-z]?\b')
BASE_RANK = {'abstract': 1, 'introduction': 2, 'model': 5, 'results': 6,
             'discussion': 4, 'other': 3, 'unknown': 3, 'proof': 0}
RELATION_NOTE = ('Earlier → later by filename year. Edges use an indexed reference plus a same-sentence '
                 'or scoped multi-sentence comparison. They are not verified claims or causal evidence.')
MULTI_CUE = re.compile(r'\b(?:unlike|contrast|however|instead|whereas|conversely|interpretable|'
                       r'endogen|exogen|generaliz|extend|relax|confirm|replicate|no longer|hold only|'
                       r'depart|differs|adopt|build on)', re.I)
RUNNING_FOOTER = re.compile(r'\b[A-Z][\w-]+(?:,\s+[A-Z][\w-]+){1,3},?\s+and\s+[A-Z][\w-]+:'
                            r'\s+[^.!?]{5,115}\s+\d{2,6}\s+[^,]{5,55},\s+(?:18|19|20)\d\d,\s+vol\.')


def normalized(text):
    text = LINE_HYPHEN.sub('', text).casefold()
    if not text.isascii():
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return ' ' + ALIAS_TOKEN.sub(' ', text).strip() + ' '


def vocabulary(path=VOCABULARY):
    import ahocorasick

    raw = path.read_bytes()
    data = json.loads(raw)
    if data['version'] != 1:
        raise ValueError('Unsupported concept vocabulary version.')
    topics, phrases = {}, defaultdict(set)
    for item in data['topics']:
        key = item['id']
        if key in topics:
            raise ValueError(f'Duplicate concept ID: {key}')
        topics[key] = item['label']
        for alias in item['aliases']:
            term = normalized(alias)
            if term.strip():
                phrases[term].add(key)
    index = ahocorasick.Automaton()
    for term, keys in phrases.items():
        index.add_word(term, (term.strip(), tuple(sorted(keys))))
    index.add_word('\x01', ('', ()))
    index.make_automaton()
    return topics, index, hashlib.sha256(raw).hexdigest()


def connect(path, write=False):
    path = path.resolve()
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, timeout=30)
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=NORMAL')
        con.executescript(SCHEMA)
    else:
        con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=15)
    con.row_factory = sqlite3.Row
    return con


def check_bindings(con, rag, path, source=None):
    config = dict(con.execute('SELECT key,value FROM config'))
    names = dict(rag.execute('SELECT key,value FROM config'))
    if (config.get('version') != VERSION or not (recorded_rag := config.get('rag'))
            or Path(recorded_rag).resolve() != path.resolve()
            or not (recorded_source := config.get('source'))
            or not (rag_source := names.get('source'))
            or Path(recorded_source).resolve() != Path(rag_source).resolve()
            or (source is not None and Path(recorded_source).resolve() != source.resolve())):
        raise ValueError('Semantic index is uninitialized or belongs to another corpus/version.')
    return config


def sentence_bounds(text, start, end):
    left = max(0, start - 430)
    right = min(len(text), end + 430)
    stops = list(SENTENCE_END.finditer(text, left, right))
    before = max((m.end() for m in stops if m.end() <= start), default=left)
    after = next((m.end() for m in stops if m.end() >= end), right)
    return before, after


def citation_matcher(refs):
    owners = defaultdict(list)
    for ref in refs:
        # The catalog's filename author hint is not a verified author list.
        names = corpus_rag.WORD.findall(ref['author'].casefold())
        if names and len(names[0]) >= 2 and ref['year']:
            owners[names[0], str(ref['year'])].append(ref)
    names = '|'.join(re.escape(n) for n in sorted({n for n, _ in owners}, key=lambda n: (-len(n), n)))
    if not names:
        return None, owners
    coauthor = r"[A-Za-zÀ-ž][A-Za-zÀ-ž'’-]*"
    return re.compile(r'\b(?P<name>' + names + r')\b'
                      r'(?:\s+et al\.|(?:\s*,\s*' + coauthor + r'){0,2}\s*,?\s+(?:and|&)\s+' + coauthor + r')?'
                      r"(?:[’']s)?\s*,?\s*(?:\(\s*(?P<narrative>(?:18|19|20)\d{2})(?:\s*[,;]\s*(?:p{1,2}\.\s*)?\d+(?:[-–]\d+)?)?\s*\)|"
                      r'\s(?P<inline>(?:18|19|20)\d{2})(?![a-z0-9]|\s*[-/]\d))', re.I), owners


def classify(left, right):
    left = left.rstrip().removesuffix('(').rstrip()
    right = right.lstrip().removeprefix(')').lstrip()
    if match := OWN_ACTION.search(left + ' '):
        action = match[1].casefold()
        return 'adopts_component' if action.startswith(('follow', 'adopt')) else 'extends_component'
    if match := RESULT_OBJECT.search(left + ' '):
        return 'supports_result' if match['verb'].lower() == 'are consistent' else 'contrasts_results'
    if LIMIT_OBJECT.search(left + ' ') and LIMIT_TAIL.search(right):
        return 'limits_result'
    if re.search(r'\b(?:unlike|in contrast (?:to|with)) (?:the (?:model|analysis|framework) (?:in|of) )?$', left + ' ', re.I):
        if CHANGE.search(right) or re.search(r'\bwe (?:make|treat|model)\b', right, re.I):
            return 'contrasts_assumptions'
    if re.search(r'\b(?:although|while|whereas)\s*$', left, re.I):
        if re.match(r'\s*(?:assum(?:e|es)|impos(?:e|es)|restrict(?:s)?)\b', right, re.I) and CHANGE.search(right):
            return 'contrasts_assumptions'
    if re.search(r'\bwe (?:confirm|replicate) (?:the )?(?:results?|findings?) (?:of|in) $', left + ' ', re.I):
        return 'supports_result'
    if re.search(r'\b(?:this is|we use|our model uses) the same (?:[\w-]+ ){0,4}'
                 r'(?:function|technology|assumption|model|strategy) as (?:in )?(?:the model of )?$',
                 left + ' ', re.I):
        return 'adopts_component'
    return None


def extract_relations(text, matcher, owners, doc, passage, page, section):
    if not matcher or section == 'endmatter' or not YEAR.search(text):
        return (), set(), 0
    matches = list(matcher.finditer(text))
    context, proposals, ambiguous = set(), [], 0
    for match in matches:
        year = match['narrative'] or match['inline']
        refs = owners.get((match['name'].casefold(), year), ())
        refs = [r for r in refs if page < r['page']]
        if len(refs) != 1:
            ambiguous += bool(refs)
            continue
        ref = refs[0]
        context.add(ref['id'])
        if not doc['year'] or not ref['year'] or ref['year'] > doc['year']:
            continue
        left, right = sentence_bounds(text, match.start(), match.end())
        before, after = text[left:match.start()], text[match.end():right]
        # A flattened section header can repeat this exact citation before the body sentence.
        repeated = next((m for m in reversed(matches) if left <= m.start() < match.start()), None)
        if repeated and re.fullmatch(r'\s*Comparison with\s*', text[left:repeated.start()], re.I):
            if repeated.groupdict() == match.groupdict():
                left = repeated.end()
                before = text[left:match.start()]
        if not CUE.search(before + after):
            continue
        if (any(m != match and left <= m.start() < right for m in matches)
                or OTHER_CITATION.search(before) or OTHER_CITATION.search(after)
                or re.search(r';\s*[A-Z][\w-]+\s', after)):
            ambiguous += 1
            continue
        if kind := classify(before, after):
            # Excerpts are verbatim within the existing PDF-text passage (not typographic transcriptions).
            proposals.append((ref['id'], doc['id'], ref['year'], doc['year'], kind,
                              passage, page, section, ref['page'], text[left:right].strip()))
    return proposals, context, ambiguous


def overlap(previous, current):
    """Require actual shared text; do not stitch columns, pages or section boundaries blindly."""
    prefix = current[:42]
    if len(prefix) < 42:
        return None
    i = previous.rfind(prefix, max(0, len(previous)-240))
    if i >= 0 and current.startswith(previous[i:]):
        return i
    return None


def expanded_relations(current, prior, matcher, owners, doc):
    passage, text, page, section, heading = current
    if not matcher or not doc['year'] or section in ('proof', 'endmatter', 'references'):
        return
    parts = [(0, passage, text)]
    if prior and prior[0]+1 == passage and prior[2:] == current[2:]:
        if (i := overlap(prior[1], text)) is not None:
            parts = [(0, prior[0], prior[1]), (i, passage, text)]
    value = parts[0][2] if len(parts)==1 else parts[0][2][:parts[1][0]] + text
    if not (MULTI_CUE.search(value) and YEAR.search(value)):
        return
    if (footer := RUNNING_FOOTER.search(value)) is not None:
        value = value[:footer.start()].rstrip()
    matches = list(matcher.finditer(value))
    if not matches:
        return
    spans = list(semantic_context.BODY_CITE.finditer(value))
    for m, kind, lo, hi, method in semantic_context.discourse_relations(value, matches, spans):
        refs = owners.get((m['name'].casefold(), m['narrative'] or m['inline']), ())
        eligible = [r for r in refs if page < r['page']]
        if len(eligible) != 1 or eligible[0]['year'] > doc['year']:
            continue
        ref = eligible[0]
        if hi-lo > 1450:
            continue
        base = next((p for p in reversed(parts) if p[0] <= lo and hi <= p[0]+len(p[2])), None)
        if base:
            evidence = [{'passage': base[1], 'page': page, 'excerpt': value[lo:hi].strip()}]
        else:
            cut = len(parts[0][2])
            evidence = [{'passage': parts[0][1], 'page': page, 'excerpt': value[lo:cut].strip()},
                        {'passage': passage, 'page': page, 'excerpt': value[cut:hi].strip()}]
        yield (ref['id'], doc['id'], ref['year'], doc['year'], kind, evidence[0]['passage'],
               page, section, ref['page'], value[lo:hi].strip(), method, json.dumps(evidence, ensure_ascii=False))


def extract_paper(rag, dest, doc, refs, fingerprint, concepts):
    key = doc['id']
    for table in ('mentions', 'statements', 'relations'):
        dest.execute(f"DELETE FROM {table} WHERE {'later' if table == 'relations' else 'paper'}=?", (key,))
    seen, claims, edges = {}, {}, {}
    matcher, owners = citation_matcher(refs)
    start = key * corpus_rag.PASSAGE_BASE
    count, unclear, contexts = 0, 0, set()
    previous = None
    for current in rag.execute('''SELECT rowid,text,page,section,heading FROM passages
                 WHERE rowid>=? AND rowid<? ORDER BY rowid''', (start, start + corpus_rag.PASSAGE_BASE)):
        current = tuple(current)
        passage, text, page, section, _ = current
        count += 1
        if section in ('references', 'endmatter'):
            previous = None
            continue
        priority = BASE_RANK.get(section, 1)
        matches = concepts.iter(normalized(text))
        for _, (alias, topics) in matches:
            rank = priority, len(alias)
            for concept in topics:
                if concept not in seen or rank > seen[concept][0]:
                    seen[concept] = (rank, (key, concept, alias, passage, page, section))
        if section != 'proof':
            for match in LABEL.finditer(text):
                if NOT_DECLARATION.search(text[max(0, match.start() - 48):match.start()]):
                    continue
                kind, label = match[1].lower(), match[2].lower()
                excerpt = text[match.start():match.end()+360].strip()
                if len(excerpt) - len(match[0]) < 28:
                    continue
                rank = priority, len(excerpt)
                candidate = kind, label
                if candidate not in claims or rank > claims[candidate][0]:
                    claims[candidate] = (rank, (key, kind, label, passage, page, section, excerpt))
            for match in ASSUME.finditer(text):
                _, end = sentence_bounds(text, match.start(), match.end())
                excerpt = text[match.start():end].strip()
                if len(excerpt) < 38:
                    continue
                candidate = 'model_assumption', f'{page}:{normalized(excerpt)[:96].strip()}'
                claims.setdefault(candidate, ((priority, len(excerpt)),
                                               (key, *candidate, passage, page, section, excerpt)))
        proposals, hits, ambiguous = extract_relations(text, matcher, owners, doc, passage, page, section)
        contexts.update(hits)
        unclear += ambiguous
        single = (e + ('explicit_single_sentence', json.dumps(
            [{'passage': e[5], 'page': e[6], 'excerpt': e[9]}], ensure_ascii=False)) for e in proposals)
        for edge in (*single, *expanded_relations(current, previous, matcher, owners, doc)):
            edge_id = edge[0], edge[4]
            rank = (edge[-2] == 'explicit_single_sentence', section in ('model', 'results', 'discussion'), len(edge[9]))
            if edge_id not in edges or rank > edges[edge_id][0]:
                edges[edge_id] = (rank, edge)
        previous = current
    dest.executemany('INSERT INTO mentions VALUES (?,?,?,?,?,?)', (row for _, row in seen.values()))
    ranked = sorted(claims.values(), key=lambda item: item[0], reverse=True)
    for assumption in (True, False):
        selected = [r for _, r in ranked if (r[1] == 'model_assumption') == assumption][: (8 if assumption else 30)]
        dest.executemany('INSERT INTO statements VALUES (?,?,?,?,?,?,?)', selected)
    dest.executemany('INSERT INTO relations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (row for _, row in edges.values()))
    dest.execute('INSERT OR REPLACE INTO scanned VALUES (?,?,?,?,?,?,?)',
                 (key, doc['stamp'], fingerprint, count, len(refs), len(contexts), unclear))


def build(args):
    if args.db.resolve() == args.corpus_db.resolve():
        raise ValueError('Use a separate semantic database.')
    start = time.monotonic()
    topic_labels, concepts, digest = vocabulary()
    with closing(corpus_rag.connect(args.corpus_db)) as rag:
        rag.execute('BEGIN')
        src = rag.execute("SELECT value FROM config WHERE key='source'").fetchone()
        if src is None or args.db.resolve() == Path(src[0]).resolve():
            raise ValueError('Corpus is unbound or semantic DB points to the source catalog.')
        with paperlist.build_lock(args.db.resolve()), closing(connect(args.db, True)) as dest:
            build_snapshot(args, rag, dest, src[0], start, topic_labels, concepts, digest)
    print('Build pass complete. Run status for measured coverage.', flush=True)


def build_snapshot(args, rag, dest, source, start, topic_labels, concepts, digest):
    # The upstream passages and links share one read snapshot throughout the pass.
    config = {'version': VERSION, 'rag': str(args.corpus_db.resolve()), 'source': source,
              'vocabulary': digest, 'concept_labels': json.dumps(topic_labels)}
    previous = dict(dest.execute('SELECT key,value FROM config'))
    if previous and previous != config:
        raise ValueError('Corpus, schema or vocabulary changed. Build into a new --db file.')
    docs = rag.execute('SELECT id,stamp,year FROM docs ORDER BY id').fetchall()
    live = {r['id'] for r in docs}
    prior = dict(dest.execute('SELECT paper,fingerprint FROM scanned'))
    recheck = ({r[0] for r in dest.execute("SELECT DISTINCT later FROM relations WHERE method <> 'explicit_single_sentence'")}
               if args.recheck_contexts else set())
    refs = defaultdict(list)
    for row in rag.execute('''SELECT l.citing,l.page,d.id,d.author,d.year FROM links l
                  JOIN docs d ON d.id=l.cited WHERE l.method='section_title_author_year'
                  ORDER BY l.citing,l.cited'''):
        refs[row['citing']].append(row)
    todo = []
    for d in docs:
        key = d['id']
        fingerprint = hashlib.sha256(repr((d['stamp'], d['year'],
                                          [tuple(r) for r in refs.get(key, ())])).encode()).hexdigest()
        if args.refresh or key in recheck or prior.get(key) != fingerprint:
            todo.append((d, fingerprint))
    if args.limit:
        todo = todo[:args.limit]
    with dest:
        dest.executemany('INSERT OR IGNORE INTO config VALUES (?,?)', config.items())
        for dead in prior.keys() - live:
            for table in ('mentions', 'statements', 'scanned'):
                dest.execute(f'DELETE FROM {table} WHERE paper=?', (dead,))
            dest.execute('DELETE FROM relations WHERE earlier=? OR later=?', (dead, dead))
    print(f'{len(docs):,} corpus PDFs; {len(todo):,} queued; {len(topic_labels)} concepts', flush=True)
    last = start
    for offset in range(0, len(todo), 128):
        batch = todo[offset:offset+128]
        with dest:
            for doc, fingerprint in batch:
                extract_paper(rag, dest, doc, refs.get(doc['id'], ()), fingerprint, concepts)
        now = time.monotonic()
        done = offset + len(batch)
        if now - last >= 15 or done == len(todo):
            print(f'{done:,}/{len(todo):,} PDFs; {now-start:.0f}s', flush=True)
            last = now


def status(con, rag):
    total = rag.execute('SELECT COUNT(*) FROM docs').fetchone()[0]
    coverage = dict(con.execute('''SELECT COUNT(*) AS scanned_pdfs,COALESCE(SUM(passages),0) AS scanned_passages,
        COALESCE(SUM(passages=0),0) AS without_body_passages,
        COALESCE(SUM(references_checked),0) AS bibliographic_pairs_screened,
        COALESCE(SUM(pairs_with_context),0) AS pairs_with_body_author_year,
        COALESCE(SUM(ambiguous_contexts),0) AS ambiguous_context_matches
        FROM scanned''').fetchone())
    coverage['corpus_pdfs'] = total
    known = dict(con.execute('SELECT paper,stamp FROM scanned'))
    coverage['scans_missing_or_stale_by_document_stamp'] = sum(
        stamp != known.get(key) for key, stamp in rag.execute('SELECT id,stamp FROM docs'))
    coverage['concepts_seen'] = con.execute('SELECT COUNT(DISTINCT concept) FROM mentions').fetchone()[0]
    coverage['concept_paper_mentions'] = con.execute('SELECT COUNT(*) FROM mentions').fetchone()[0]
    coverage['pdfs_with_concepts'] = con.execute('SELECT COUNT(DISTINCT paper) FROM mentions').fetchone()[0]
    coverage['statement_candidates'] = dict(con.execute('SELECT kind,COUNT(*) FROM statements GROUP BY kind'))
    coverage['pdfs_with_statements'] = con.execute('SELECT COUNT(DISTINCT paper) FROM statements').fetchone()[0]
    coverage['semantic_relation_candidates'] = dict(con.execute('SELECT kind,COUNT(*) FROM relations GROUP BY kind'))
    coverage['relation_extraction_methods'] = dict(con.execute('SELECT method,COUNT(*) FROM relations GROUP BY method'))
    coverage['distinct_relation_pairs'] = con.execute(
        'SELECT COUNT(*) FROM (SELECT DISTINCT earlier,later FROM relations)').fetchone()[0]
    coverage['note'] = 'Counts are machine candidates. A fresh index still has incomplete concept and relation recall.'
    return coverage


def document(rag, key):
    row = rag.execute('SELECT id,title,author,year AS filename_year,journal,relpath,stamp FROM docs WHERE id=?',
                      (key,)).fetchone()
    return dict(row) if row else None


def fresh(con, doc):
    if not doc:
        return False
    row = con.execute('SELECT stamp FROM scanned WHERE paper=?', (doc['id'],)).fetchone()
    return bool(row and row['stamp'] == doc['stamp'])


def public_doc(doc):
    return {k: v for k, v in doc.items() if k != 'stamp'}


def edge_info(con, rag, row):
    early, late = document(rag, row['earlier']), document(rag, row['later'])
    if not early or not fresh(con, late):
        return None
    if (early['filename_year'], late['filename_year']) != (row['earlier_year'], row['later_year']):
        return None
    ref = rag.execute('''SELECT page FROM links WHERE citing=? AND cited=? AND method='section_title_author_year' ''',
                      (row['later'], row['earlier'])).fetchone()
    if not ref or ref['page'] != row['ref_page']:
        return None
    return dict(row) | {'earlier_paper': public_doc(early), 'later_paper': public_doc(late),
                        'evidence_pdf': late['relpath'], 'state': 'machine_candidate',
                        'evidence_pieces': json.loads(row['evidence_pieces'])}


def adjacent(con, node, direction, limit):
    if direction in ('past', 'both'):
        yield from con.execute('''SELECT * FROM relations WHERE later=?
            ORDER BY earlier_year DESC,earlier,page,kind LIMIT ?''', (node, limit))
    if direction in ('future', 'both'):
        yield from con.execute('''SELECT * FROM relations WHERE earlier=?
            ORDER BY later_year,later,page,kind LIMIT ?''', (node, limit))


def walk(con, rag, seeds, direction, depth, limit):
    queue = deque((s, 0) for s in seeds)
    seen, emitted, edges = set(seeds), set(), []
    while queue and len(edges) < limit:
        node, hop = queue.popleft()
        if hop >= depth:
            continue
        for row in adjacent(con, node, direction, min(limit, 12)):
            key = row['earlier'], row['later'], row['kind']
            if key not in emitted and (edge := edge_info(con, rag, row)):
                emitted.add(key)
                edges.append(edge | {'hop': hop + 1})
                other = row['earlier'] if row['later'] == node else row['later']
                if other not in seen:
                    seen.add(other)
                    queue.append((other, hop + 1))
            if len(edges) >= limit:
                break
    return sorted(edges, key=lambda e: (e['later_year'], e['earlier_year'], e['later'], e['earlier'], e['kind']))


def paths(con, rag, older, later, depth):
    early, late = document(rag, older), document(rag, later)
    if not early or not late or older == later:
        raise ValueError('Supply two distinct, valid numeric corpus paper IDs.')
    y1, y2 = early['filename_year'], late['filename_year']
    if not y1 or not y2 or y1 > y2:
        raise ValueError('Supply the older paper first; both need a filename year.')
    queue = deque([(older, (older,), ())])
    result, expanded, limited = [], 0, False
    while queue and len(result) < 8:
        node, seen, chain = queue.popleft()
        if node == later:
            result.append({'papers': list(seen), 'relations': list(chain)})
            continue
        if len(chain) >= depth:
            continue
        rows = con.execute('''SELECT * FROM relations WHERE earlier=? AND later_year<=?
            ORDER BY (later=?) DESC,later_year,later,kind LIMIT 41''', (node, y2, later)).fetchall()
        limited |= len(rows) > 40
        for r in rows[:40]:
            if r['later'] in seen:
                continue
            if expanded >= 500:
                limited = True
                break
            if edge := edge_info(con, rag, r):
                expanded += 1
                queue.append((r['later'], (*seen, r['later']), (*chain, edge)))
    return {'from': public_doc(early), 'to': public_doc(late), 'paths': result, 'bounded': limited or bool(queue),
            'note': RELATION_NOTE + ' A missing path does not establish novelty.'}


def contextualize(con, rag, config, terms, seeds, direction, depth, limit):
    labels, concepts, digest = vocabulary()
    if digest != config.get('vocabulary'):
        raise ValueError('Concept vocabulary differs from the built semantic index.')
    if not terms and not seeds:
        return {'available': True, 'concepts': [], 'timeline': [], 'relation_candidates': [],
                'note': 'Provide English retrieval terms or paper seeds.'}
    concept_ids = sorted({c for t in terms for _, (_, keys) in concepts.iter(normalized(t)) for c in keys})
    topic_data = [{'id': k, 'label': labels[k], 'indexed_papers':
                   con.execute('SELECT COUNT(*) FROM mentions WHERE concept=?', (k,)).fetchone()[0]}
                  for k in concept_ids]
    timeline = []
    seeds = list(dict.fromkeys(seeds))[:12]
    edges = walk(con, rag, seeds, direction, min(depth, 3), min(limit, 24))
    chronological = seeds + [e['earlier'] for e in edges] + [e['later'] for e in edges]
    focus = list(dict.fromkeys(chronological))[:16]
    for key in focus:
        doc = document(rag, key)
        if not fresh(con, doc):
            continue
        rows = con.execute('SELECT * FROM mentions WHERE paper=? ORDER BY concept', (key,))
        found = []
        for row in rows:
            if concept_ids and row['concept'] not in concept_ids:
                continue
            passage = rag.execute('SELECT text FROM passages WHERE rowid=?', (row['passage'],)).fetchone()
            if passage:
                found.append(dict(row) | {'excerpt': passage[0]})
            if len(found) >= 3:
                break
        statements = []
        for query in ('kind=\'model_assumption\'', 'kind<>\'model_assumption\''):
            statements.extend(dict(r) for r in con.execute(f'''SELECT * FROM statements
                WHERE paper=? AND {query} ORDER BY page,kind,label LIMIT 2''', (key,)))
        if found or statements or key in seeds:
            timeline.append({'paper': public_doc(doc), 'concept_mentions': found, 'statement_candidates': statements})
    timeline.sort(key=lambda r: (r['paper']['filename_year'] is None, r['paper']['filename_year'] or 0, r['paper']['id']))
    return {'available': True, 'seeds': seeds, 'concepts': topic_data, 'timeline': timeline,
            'relation_candidates': edges, 'scanned_pdfs': con.execute('SELECT COUNT(*) FROM scanned').fetchone()[0],
            'corpus_pdfs': rag.execute('SELECT COUNT(*) FROM docs').fetchone()[0],
            'note': RELATION_NOTE + ' Timeline covers the selected neighborhood; concept hits do not date invention.'}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    p.add_argument('--corpus-db', type=Path, default=corpus_rag.DEFAULT_DB)
    sub = p.add_subparsers(dest='cmd', required=True)
    q = sub.add_parser('build')
    q.add_argument('--limit', type=int)
    q.add_argument('--refresh', action='store_true')
    q.add_argument('--recheck-contexts', action='store_true', help='recheck papers with existing discourse candidates')
    sub.add_parser('status')
    q = sub.add_parser('path')
    q.add_argument('older', type=int)
    q.add_argument('later', type=int)
    q.add_argument('--depth', type=int, choices=range(1, 5), default=3)
    return p


def main():
    paperlist.configure_output()
    args = parser().parse_args()
    try:
        if args.cmd == 'build':
            if args.limit is not None and args.limit <= 0:
                raise ValueError('--limit must be positive.')
            build(args)
            return 0
        with closing(connect(args.db)) as con, closing(corpus_rag.connect(args.corpus_db)) as rag:
            con.execute('BEGIN')
            rag.execute('BEGIN')
            check_bindings(con, rag, args.corpus_db)
            result = status(con, rag) if args.cmd == 'status' else paths(con, rag, args.older, args.later, args.depth)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error, ImportError) as exc:
        print(f'corpus_semantics: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
