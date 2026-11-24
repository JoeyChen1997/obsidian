"""Index what a paper explicitly attributes to another paper, with source pages."""

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
import sys
import time

import corpus_rag
import paperlist
from corpus_semantics import citation_matcher
from semantic_context import BODY_CITE, sentences, vocabulary


DEFAULT_DB = paperlist.DEFAULT_DB.with_name('research-citation-claims.sqlite3')
VERSION = '1'
SCHEMA = '''
CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scanned (paper INTEGER PRIMARY KEY, fingerprint TEXT NOT NULL, stamp TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claims (
 citing INTEGER NOT NULL, cited INTEGER NOT NULL, kind TEXT NOT NULL, page INTEGER NOT NULL,
 passage INTEGER NOT NULL, section TEXT NOT NULL, ref_page INTEGER NOT NULL, excerpt TEXT NOT NULL,
 PRIMARY KEY(citing,cited,kind,page)
);
CREATE INDEX IF NOT EXISTS claims_incoming ON claims(cited,citing);
'''
VERBS = re.compile(r'^\s*(?:(?:also|explicitly|instead|theoretically|jointly|originally|first|'
                   r'analytically|in turn|in their model)\s+)?'
                   r'(?P<verb>assum(?:e|es|ed)|postulat(?:e|es|ed)|impos(?:e|es|ed)|'
                   r'show(?:s|ed)?|find(?:s)?|found|demonstrat(?:e|es|ed)|establish(?:es|ed)?|'
                   r'prov(?:e|es|ed)|deriv(?:e|es|ed)|predict(?:s|ed)?|obtain(?:s|ed)?|'
                   r'develop(?:s|ed)?|construct(?:s|ed)?|propos(?:e|es|ed)|introduc(?:e|es|ed)|'
                   r'build(?:s)?|model(?:s|ed|led)?)\b', re.I)
MODEL = re.compile(r'\b(?:model|equilibrium|game|mechanism|framework|assumption|constraint|'
                   r'information structure|demand function|distribution|pricing|welfare|profit|'
                   r'price competition|firm|consumer|market|buyer|seller|retailer|supplier|'
                   r'exogen\w*|endogen\w*|bargaining|incentiv\w*)s?\b', re.I)
THEORY = re.compile(r'\b(?:model|equilibrium|theoretic\w*|lemma|proposition|theorem|'
                    r'comparative statics|welfare|pure strateg\w*|mixed strateg\w*)s?\b', re.I)
YEAR = re.compile(r'(?:18|19|20)\d{2}')
POSS = re.compile(r"(?:[’']s)\s*$")
SENTENCE_LEAD = re.compile(r'^(?:\d{1,3}\s*)?(?:(?:first|second|finally|however|for example|for instance|'
                           r'in contrast|similarly|relatedly|in particular|indeed|specifically|moreover|'
                           r'in this literature|on the other hand|by contrast)\s*,\s*)?$', re.I)
MODEL_LEAD = re.compile(r'^(?:\d{1,3}\s*)?In (?:the |a )?(?:model|framework|setting|game) '
                        r'(?:of|in|developed by)\s*$', re.I)
NOISE = re.compile(r'^\s*(?:this paper|our model|we|our results)\b', re.I)
ATTRIBUTION_WORDS = set('show shows demonstrated demonstrate found find finds assume assumes '
                        'always provides provide develops paper section theorem proposition'
                        .split())
PRIMARY_SECTIONS = {'introduction', 'abstract', 'discussion', 'model', 'results', 'other', 'unknown'}
NOTE = ('An attribution is the citing authors’ account of a named paper, not a verified result, '
        'a claim of priority, or evidence of model inheritance. Cited-source leads are retrieval hits only.')


def connect(path, write=False):
    path = path.resolve()
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, timeout=30)
        con.executescript('PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;' + SCHEMA)
    else:
        con = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def binding(rag, path):
    source = rag.execute("SELECT value FROM config WHERE key='source'").fetchone()
    if not source:
        raise ValueError('RAG index has no source catalog.')
    return {'version': VERSION, 'rag': str(path.resolve()), 'source': source[0]}


def check_binding(con, rag, path):
    if dict(con.execute('SELECT key,value FROM config')) != binding(rag, path):
        raise ValueError('Citation attributions index belongs to another RAG index.')


def extract(text, matcher, owners, citing, passage, page, section):
    if not YEAR.search(text):
        return
    matches = list(matcher.finditer(text))
    if not matches:
        return
    for a, b in sentences(text):
        known = [m for m in matches if a <= m.start() < b]
        if len(known) != 1:
            continue
        m = known[0]
        if POSS.search(m[0]):
            continue
        sentence = text[a:b].strip()
        before, after = text[a:m.start()].strip(), text[m.end():b].lstrip(' ),')
        if not 42 <= len(sentence) <= 800 or not 30 <= len(after.strip()) or NOISE.search(after):
            continue
        if BODY_CITE.search(before) or BODY_CITE.search(after):
            continue
        refs = [r for r in owners.get((m['name'].casefold(),m['narrative'] or m['inline']), ()) if page < r['page']]
        if len(refs) != 1:
            continue
        if MODEL_LEAD.fullmatch(before) and MODEL.search(after):
            kind = 'attributed_model_setup'
        elif SENTENCE_LEAD.fullmatch(before) and (verb := VERBS.match(after)) and MODEL.search(after[verb.end():]):
            tag, claim = verb['verb'].lower(), after[verb.end():].strip()
            if tag.startswith(('assum','postulat','impos')):
                kind = 'attributed_assumption'
            elif tag.startswith(('show','find','found','demonstrat','establish','prov','deriv','predict','obtain')):
                kind = 'attributed_theory_result' if THEORY.search(claim) else 'attributed_result_unspecified'
            else:
                if not THEORY.search(claim) and not re.search(r'\b(?:mechanism|game|framework)\b',claim,re.I):
                    continue
                kind = 'attributed_model_setup'
        else:
            continue
        yield (citing, refs[0]['id'], kind, page, passage, section, refs[0]['page'], sentence)


def build(rag_path, db, limit=None):
    if rag_path.resolve() == db.resolve():
        raise ValueError('Use a separate attribution DB.')
    start = time.monotonic()
    with closing(corpus_rag.connect(rag_path)) as rag:
        rag.execute('BEGIN')
        config = binding(rag, rag_path)
        if db.resolve() == Path(config['source']).resolve():
            raise ValueError('Use a separate attribution DB.')
        with paperlist.build_lock(db.resolve()), closing(connect(db, True)) as dest:
            old = dict(dest.execute('SELECT key,value FROM config'))
            if old and old != config:
                raise ValueError('Attribution index belongs to a different corpus/schema.')
            docs = rag.execute('SELECT id,stamp,year FROM docs ORDER BY id').fetchall()
            prior = dict(dest.execute('SELECT paper,fingerprint FROM scanned'))
            refs = defaultdict(list)
            for row in rag.execute('''SELECT l.citing,l.page,d.id,d.author,d.year FROM links l
                JOIN docs d ON d.id=l.cited WHERE l.method='section_title_author_year'
                ORDER BY l.citing,l.cited'''):
                refs[row['citing']].append(row)
            live = {r['id'] for r in docs}
            todo = []
            for key, stamp, year in docs:
                finger = hashlib.sha256(repr((stamp,year,[tuple(r) for r in refs.get(key,())])).encode()).hexdigest()
                if prior.get(key) != finger:
                    todo.append((key,stamp,year,finger))
            todo = todo[:limit]
            with dest:
                dest.executemany('INSERT OR IGNORE INTO config VALUES (?,?)',config.items())
                for key in prior.keys()-live:
                    dest.execute('DELETE FROM scanned WHERE paper=?',(key,))
                    dest.execute('DELETE FROM claims WHERE citing=? OR cited=?',(key,key))
            print(f'{len(docs):,} corpus PDFs; {len(todo):,} queued for attributed claims', flush=True)
            last = start
            for idx in range(0,len(todo),256):
                batch = todo[idx:idx+256]
                with dest:
                    for key,stamp,year,finger in batch:
                        dest.execute('DELETE FROM claims WHERE citing=?',(key,))
                        targets = [r for r in refs.get(key,()) if not year or r['year'] and r['year']<=year]
                        matcher, owners = citation_matcher(targets)
                        candidates = {}
                        if matcher:
                            lo = key*corpus_rag.PASSAGE_BASE
                            for passage,text,page,section in rag.execute('''SELECT rowid,text,page,section FROM passages
                                      WHERE rowid>=? AND rowid<? ORDER BY rowid''',(lo,lo+corpus_rag.PASSAGE_BASE)):
                                if section not in PRIMARY_SECTIONS:
                                    continue
                                for item in extract(text,matcher,owners,key,passage,page,section):
                                    claim_key = (item[1],item[2],page)
                                    old_item = candidates.get(claim_key)
                                    if not old_item or len(item[-1]) > len(old_item[-1]):
                                        candidates[claim_key] = item
                        dest.executemany('INSERT INTO claims VALUES (?,?,?,?,?,?,?,?)', candidates.values())
                        dest.execute('INSERT OR REPLACE INTO scanned VALUES (?,?,?)',(key,finger,stamp))
                now = time.monotonic()
                if now-last >= 15 or idx+len(batch)==len(todo):
                    print(f'{idx+len(batch):,}/{len(todo):,}; {now-start:.0f}s',flush=True)
                    last = now


def status(con, rag):
    previous = dict(con.execute('SELECT paper,stamp FROM scanned'))
    coverage = sum(stamp == previous.get(key) for key,stamp in rag.execute('SELECT id,stamp FROM docs'))
    return {'corpus_pdfs':rag.execute('SELECT COUNT(*) FROM docs').fetchone()[0], 'scanned_current_pdfs':coverage,
            'attributions':dict(con.execute('SELECT kind,COUNT(*) FROM claims GROUP BY kind')),
            'distinct_citation_pairs':con.execute(
                'SELECT COUNT(*) FROM (SELECT DISTINCT citing,cited FROM claims)').fetchone()[0], 'note':NOTE}


def source_leads(rag, paper, excerpt, query, limit=2):
    """Find candidate pages in the cited paper using the attributed claim and research query."""
    clean = BODY_CITE.sub(' ', excerpt)
    keywords = vocabulary(clean) - ATTRIBUTION_WORDS
    if len(keywords) < 3:
        return []
    lo = paper * corpus_rag.PASSAGE_BASE
    pages, frequencies = [], Counter()
    for row in rag.execute('''SELECT rowid,page,section,text FROM passages WHERE rowid>=? AND rowid<?
                              ORDER BY rowid''', (lo, lo+corpus_rag.PASSAGE_BASE)):
        if row['section'] in ('abstract','introduction','endmatter','references'):
            continue
        matches = vocabulary(row['text']) & keywords
        frequencies.update(matches)
        if len(matches) >= 3:
            pages.append((row, matches))
    if not pages:
        return []
    scored = []
    for row, matches in pages:
        terms = sorted(matches, key=lambda w: (frequencies[w], w))
        relevance = sum((1.4 if w in query else 1.0)/(1+math.log(frequencies[w])) for w in matches)
        if row['section'] in ('model','results','proof'):
            relevance *= 1.15
        scored.append((relevance, row['rowid'], row, terms))
    seen, results = set(), []
    for _, _, row, match in sorted(scored, key=lambda x:(-x[0],x[1])):
        if row['page'] in seen:
            continue
        seen.add(row['page'])
        results.append({'page':row['page'],'passage':row['rowid'],'section':row['section'],
                        'excerpt':row['text'],'matched_words':match[:12],
                        'state':'cited_source_retrieval_lead'})
        if len(results)>=limit:
            break
    return results


def search(con, rag, seeds, terms, direction, limit=12):
    query = vocabulary(' '.join(terms))
    rows = {}
    for anchor in list(dict.fromkeys(seeds))[:10]:
        fields = ('citing',) if direction=='past' else ('cited',) if direction=='future' else ('citing','cited')
        for side in fields:
            for row in con.execute(f'SELECT * FROM claims WHERE {side}=? ORDER BY citing,cited,kind,page', (anchor,)):
                key = row['citing'],row['cited'],row['kind']
                overlap = len(query & vocabulary(row['excerpt']))
                weights = {'attributed_theory_result':2,'attributed_assumption':2,'attributed_model_setup':1}
                rank = (overlap, weights.get(row['kind'],0), -row['page'])
                if not (prior := rows.get(key)) or rank > prior[0]:
                    rows[key] = rank,row
    results, pairs = [], Counter()
    for _, row in sorted(rows.values(), key=lambda t:t[0], reverse=True):
        a,b = row['citing'],row['cited']
        if pairs[a,b] >= 2:
            continue
        docs = dict((d['id'],dict(d)) for d in rag.execute(
            'SELECT id,title,year AS filename_year,stamp,relpath FROM docs WHERE id IN (?,?)',(a,b)))
        if len(docs)!=2:
            continue
        scan = con.execute('SELECT stamp FROM scanned WHERE paper=?',(a,)).fetchone()
        ref = rag.execute("SELECT page FROM links WHERE citing=? AND cited=? AND method='section_title_author_year'",
                          (a,b)).fetchone()
        if not scan or not ref or docs[a]['stamp'] != scan[0] or ref[0] != row['ref_page']:
            continue
        for d in docs.values():
            d.pop('stamp')
        results.append(dict(row) | {'citing_paper':docs[a],'cited_paper':docs[b],'state':'attribution_candidate',
                                    'cited_source_leads':source_leads(rag,b,row['excerpt'],query)})
        pairs[a,b] += 1
        if len(results)>=limit:
            break
    return {'available':True,'scanned_pdfs':con.execute('SELECT COUNT(*) FROM scanned').fetchone()[0],
            'claims':results,'note':NOTE}


def main():
    paperlist.configure_output()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',type=Path,default=DEFAULT_DB)
    p.add_argument('--corpus-db',type=Path,default=corpus_rag.DEFAULT_DB)
    sub = p.add_subparsers(dest='cmd',required=True)
    b = sub.add_parser('build')
    b.add_argument('--limit',type=int)
    sub.add_parser('status')
    a = p.parse_args()
    try:
        if a.cmd=='build':
            if a.limit is not None and a.limit<1:
                raise ValueError('Build limit must be positive.')
            build(a.corpus_db,a.db,a.limit)
        else:
            with closing(corpus_rag.connect(a.corpus_db)) as rag, closing(connect(a.db)) as con:
                check_binding(con,rag,a.corpus_db)
                print(json.dumps(status(con,rag),ensure_ascii=False,indent=2))
    except (OSError,ValueError,sqlite3.Error) as exc:
        print(f'citation_claims: {exc}',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
