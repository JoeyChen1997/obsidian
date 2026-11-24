"""Build/query a section-passage RAG index and candidate citation graph for Paperlist."""

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import unicodedata

import paperlist

DEFAULT_DB = paperlist.DEFAULT_DB.with_name('research-corpus.sqlite3')
for dependency_dir in ('citation-deps','rag-deps'):
    local_deps = DEFAULT_DB.parent / dependency_dir
    if local_deps.is_dir():
        sys.path.append(str(local_deps))

SCHEMA = '''
CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS docs (
 id INTEGER PRIMARY KEY, relpath TEXT NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL,
 year INTEGER, journal TEXT NOT NULL, stamp TEXT NOT NULL, abstract TEXT,
 page_count INTEGER NOT NULL, heading_count INTEGER NOT NULL, bibliography TEXT NOT NULL,
 has_abstract INTEGER NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(
 text, paper UNINDEXED, page UNINDEXED, section UNINDEXED, heading UNINDEXED,
 tokenize='unicode61 remove_diacritics 2');
CREATE TABLE IF NOT EXISTS links (
 citing INTEGER NOT NULL, cited INTEGER NOT NULL, page INTEGER NOT NULL,
 method TEXT NOT NULL, excerpt TEXT NOT NULL, PRIMARY KEY(citing,cited));
CREATE INDEX IF NOT EXISTS links_incoming ON links(cited,citing);
'''
VERSION = '1'
PASSAGE_BASE = 1_000_000
WORD = re.compile(r'[^\W_]+')
CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
HEADER = re.compile(r'^(?:(?P<number>(?:\d+(?:\.\d+)*|[IVX]{1,6}|[A-Z])\s*[.)]?)[ \t]+)?(?P<title>[A-Za-z][^\n]{0,105})$')
REF = re.compile(r'^(?:references(?: and notes)?|literature cited|bibliography|works cited)\s*[:.]?$', re.I)
ABSTRACT = re.compile(r'^abstract(?:\s*[.:—–-]\s*|\s+|$)', re.I)
DOI = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.I)
SECTION_WORDS = {
    'introduction': r'^(introduction|motivation|background|overview|related (?:literature|work|research)|literature review)\b',
    'proof': r'^(appendix|appendices|proof|proofs|supplementary)\b',
    'model': r'^(?:(?:the|a|our|basic|baseline|benchmark|theoretical|economic) )?(model|framework|setup|set.up|setting|game|environment|demand|methodology|methods|empirical strategy|identification|data)\b',
    'results': r'^(?:(?:main|the|empirical|equilibrium|theoretical) )?(results|findings|equilibrium|analysis|comparative statics|welfare|counterfactuals|estimation|extensions|robustness|competition)\b',
    'discussion': r'^(discussion|conclusion|conclusions|final remarks|limitations|implications|summary)\b',
    'endmatter': r'^(acknowledgments|acknowledgements|endnotes|footnotes)\b',
}
SECTIONS = ('abstract', *SECTION_WORDS, 'references', 'unknown', 'other')


def clean(value):
    return CONTROL.sub('', unicodedata.normalize('NFKC', value)).replace('\xad', '')


def norm(value):
    value = unicodedata.normalize('NFKD', clean(value)).casefold()
    return ' '.join(WORD.findall(''.join(c for c in value if not unicodedata.combining(c))))


def citation_norm(value):
    return norm(value).replace(' & ', ' and ')


def normalized_title(value):
    return re.sub(r'^(?:research note|research article|original article|express)\s+', '', citation_norm(value))


def section_heading(line):
    s = line.strip()
    if len(s) > 112 and not s[:8].casefold().startswith('abstract'):
        return None
    if REF.fullmatch(s):
        return 'references', s, ''
    if m := ABSTRACT.match(s):
        # A bare heading or the publisher's “Abstract.” inline label.
        if not s[m.end():] or re.match(r'^abstract\s*[.:—–-]', s, re.I):
            return 'abstract', 'Abstract', s[m.end():]
    match = HEADER.fullmatch(s)
    if not match:
        return None
    title = match['title']
    if len(title.split()) > 12 or title.endswith((',', ';', ':', '?')):
        return None
    words = title.rstrip('.').casefold()
    for family, regex in SECTION_WORDS.items():
        if re.search(regex, words):
            if match['number'] or len(title.split()) <= 4 or (title.istitle() and not title.endswith('.')):
                return family, title, ''
    if match['number'] and title.istitle() and len(title.split()) <= 8:
        return 'other', title, ''
    return None


def blocks(body, state, heads):
    section, heading = state
    lines = []
    for line in clean(body).splitlines():
        hit = section_heading(line)
        if section == 'references' and hit and hit[0] not in ('proof', 'endmatter', 'references'):
            hit = None
        if hit:
            if lines:
                yield section, heading, '\n'.join(lines)
            section, heading, rest = hit
            heads.append(section)
            lines = [rest] if rest else []
        else:
            lines.append(line)
    if lines:
        yield section, heading, '\n'.join(lines)
    state[:] = [section, heading]


def chunks(value, length=1050, overlap=180):
    text = re.sub(r'\s+', ' ', value).strip()
    if not text:
        return
    i = 0
    while i < len(text):
        end = min(len(text), i + length)
        if end < len(text):
            choices = [text.rfind(p, i + length * 2 // 3, end + 1) for p in ('. ', '? ', '! ')]
            cut = max(choices)
            end = cut + 1 if cut >= 0 else (text.rfind(' ', i + length // 2, end + 1) + 1 or end)
        yield text[i:end].strip()
        if end == len(text):
            break
        start = text.find(' ', end - overlap, end)
        i = start + 1 if start >= 0 else end


def connect(path, write=False):
    path = path.resolve()
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, timeout=30)
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=NORMAL')
        con.execute('PRAGMA cache_size=-98304')
        con.executescript(SCHEMA)
    else:
        if not path.is_file():
            raise ValueError(f'Corpus RAG index not found: {path}. Run corpus_rag.py build first.')
        con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=15)
    con.row_factory = sqlite3.Row
    return con


def title_matcher(rows):
    import ahocorasick
    titles = defaultdict(list)
    for row in rows:
        if row['year'] is None or not row['author_hint']:
            continue
        title = normalized_title(row['title_hint'])
        tokens = title.split()
        if len(tokens) >= 3 and len(title) >= 15:
            author_words = norm(row['author_hint']).split()
            names = tuple(t for t in author_words if len(t) >= 3)
            if names:
                titles[title].append((row['id'], row['year'], names))
    matcher = ahocorasick.Automaton()
    for title, ids in titles.items():
        matcher.add_word(' ' + title + ' ', (title, ids))
    # The extra sentinel also makes an empty fixture valid.
    matcher.add_word('\x01', ('', []))
    matcher.make_automaton()
    return matcher


def resolve_refs(matcher, row, refs, method):
    if not refs:
        return {}
    parts = []
    offset = 0
    pages = []
    for page, raw in refs:
        pages.append((offset, page))
        part = citation_norm(raw) + ' '
        parts.append(part)
        offset += len(part)
    full = ' ' + ''.join(parts)
    from bisect import bisect_right
    offsets = [start for start, _ in pages]
    matches = {}
    for end, (title, candidates) in matcher.iter(full):
        start = end - len(title)
        lead = full[max(0, start - 220):start]
        follow = full[end:min(len(full), end + 80)]
        lead_words = set(lead.split())
        after_words = set(follow.split())
        viable = [(key, year) for key, year, names in candidates if key != row['id']
                  and (not row['year'] or year <= row['year'] + 1)
                  and (str(year) in lead_words or str(year) in after_words)
                  and bool(set(names) & lead_words)]
        if len(viable) != 1:
            continue  # Do not choose arbitrarily between alternate versions/ambiguous titles.
        key, _ = viable[0]
        page = pages[max(0, bisect_right(offsets, start - 1) - 1)][1]
        excerpt = full[max(0, start - 95):min(len(full), end + 95)].strip()
        matches.setdefault(key, (row['id'], key, page, method, excerpt))
    return matches


def stamp(row):
    return f"{row['mtime_ns']}:{row['size']}:{row['text_pages']}:{row['status']}:{row['relpath']}"


def process(con, row, page_rows, matcher):
    state = ['unknown', '']
    headings = []
    citations = []
    tail = []
    abstract = []
    fallback = []
    passages = []
    for page, body in page_rows:
        tail.append((page, body))
        if len(tail) > 6:
            tail.pop(0)
        if page <= 2 and len(fallback) < 2:
            fallback.append(' '.join(clean(body).split())[:1100])
        for section, heading, part in blocks(body, state, headings):
            if section == 'references':
                citations.append((page, part))
                continue
            if section == 'abstract' and page <= 3 and len(abstract) < 4:
                abstract.append(' '.join(part.split())[:1600])
            # Keep every body page, including unmatched headings and OCR text.
            for passage in chunks(part):
                passages.append((passage, row['id'], page, section, heading))
    links = resolve_refs(matcher, row, citations or tail, 'section_title_author_year' if citations else 'tail_title_author_year')
    abstract_text = ' '.join(abstract)[:1600] or ' '.join(fallback)[:950] or None
    bib = 'heading' if citations else 'tail' if tail else 'unavailable'
    if len(passages) >= PASSAGE_BASE:
        raise ValueError(f'Too many passages for paper id {row["id"]}')
    old_start = row['id'] * PASSAGE_BASE
    con.execute('DELETE FROM passages WHERE rowid>=? AND rowid<?', (old_start, old_start + PASSAGE_BASE))
    con.execute('DELETE FROM links WHERE citing=?', (row['id'],))
    con.executemany('INSERT INTO passages(rowid,text,paper,page,section,heading) VALUES (?,?,?,?,?,?)',
                    ((old_start + i, *p) for i, p in enumerate(passages)))
    con.executemany('INSERT INTO links VALUES (?,?,?,?,?)', links.values())
    con.execute('INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (row['id'], row['relpath'], row['title_hint'], row['author_hint'], row['year'], row['journal'], stamp(row),
                 abstract_text, len(page_rows), len(headings), bib, int(bool(abstract))))
    return len(passages), len(links)


def build(args):
    if args.source.resolve() == args.db.resolve():
        raise ValueError('Keep the RAG index separate from the original index.')
    start = time.monotonic()
    with paperlist.build_lock(args.db.resolve()), closing(paperlist.connect(args.source)) as src, closing(connect(args.db, True)) as dest:
        source_name = str(args.source.resolve())
        config = dict(dest.execute('SELECT * FROM config'))
        if config and (config.get('source') != source_name or config.get('version') != VERSION):
            raise ValueError('The RAG index belongs to a different source/schema; use another --db.')
        # Snapshot the source so changes between document rows and indexed pages cannot mix.
        src.execute('BEGIN')
        rows = src.execute("SELECT * FROM papers WHERE status NOT IN ('missing','pending') ORDER BY id").fetchall()
        previous = dict(dest.execute('SELECT id,stamp FROM docs'))
        live = {row['id'] for row in rows}
        with dest:
            dest.executemany('INSERT OR IGNORE INTO config VALUES (?,?)', [('source', source_name), ('version', VERSION)])
            for dead in previous.keys() - live:
                dest.execute('DELETE FROM links WHERE citing=? OR cited=?', (dead, dead))
                dest.execute('DELETE FROM passages WHERE rowid>=? AND rowid<?',
                             (dead * PASSAGE_BASE, (dead + 1) * PASSAGE_BASE))
                dest.execute('DELETE FROM docs WHERE id=?', (dead,))
        todo = [row for row in rows if args.refresh or previous.get(row['id']) != stamp(row)]
        if args.limit:
            todo = todo[:args.limit]
        matcher = title_matcher(rows)
        print(f'Corpus {len(rows):,} eligible PDFs; queued {len(todo):,}', flush=True)
        passages = edges = 0
        last = start
        for offset in range(0, len(todo), 128):
            batch = todo[offset:offset + 128]
            with dest:
                for row in batch:
                    lo = row['id'] * paperlist.PAGE_STRIDE
                    page_rows = src.execute('SELECT pdf_page,body FROM page_index WHERE rowid>=? AND rowid<? ORDER BY rowid',
                                            (lo, lo + paperlist.PAGE_STRIDE)).fetchall()
                    p, e = process(dest, row, page_rows, matcher)
                    passages += p
                    edges += e
            done = offset + len(batch)
            now = time.monotonic()
            if now - last > 10 or done == len(todo):
                print(f'{done:,}/{len(todo):,} PDFs; {passages:,} passages; {edges:,} candidate citations; {now-start:.0f}s', flush=True)
                last = now
    print('Build pass complete. Run status for measured coverage.', flush=True)


def stats(con):
    result = dict(con.execute('''SELECT COUNT(*) AS papers, SUM(page_count) AS indexed_source_pages,
        SUM(page_count=0) AS without_searchable_text, SUM(heading_count>0) AS with_recognized_heading,
        SUM(has_abstract) AS with_recognized_abstract, SUM(bibliography='heading') AS with_bibliography_heading
        FROM docs''').fetchone())
    result['passages'] = con.execute('SELECT COUNT(*) FROM passages').fetchone()[0]
    result['citation_candidates'] = dict(con.execute('SELECT method,COUNT(*) FROM links GROUP BY method'))
    result['papers_with_outgoing'] = con.execute('SELECT COUNT(DISTINCT citing) FROM links').fetchone()[0]
    result['papers_with_incoming'] = con.execute('SELECT COUNT(DISTINCT cited) FROM links').fetchone()[0]
    return result


def passage_search(con, terms, phrases=(), journals=(), section=None, limit=10):
    filters = []
    params = []
    if journals:
        filters.append(f"upper(d.journal) IN ({','.join('?' for _ in journals)})")
        params.extend(v.upper() for v in journals)
    if section:
        filters.append('p.section=?')
        params.append(section)
    extra = ''.join(f' AND {item}' for item in filters)
    scores = defaultdict(float)
    records = {}
    hit_counts = {}
    seen_queries = list(dict.fromkeys([*terms, *phrases]))
    for term in seen_queries:
        words = WORD.findall(clean(term))
        if not words:
            continue
        query = ('"' + ' '.join(words) + '"' if term in phrases else ' AND '.join(f'"{word}"' for word in words))
        seen_papers = set()
        for r in con.execute(f'''SELECT p.rowid, p.paper, p.page, p.section, p.heading, p.text,
                 d.relpath,d.title,d.author,d.year,d.journal
                 FROM passages p JOIN docs d ON d.id=p.paper
                 WHERE passages MATCH ? {extra} ORDER BY rank LIMIT 160''', [query, *params]):
            d = dict(r)
            pid = d['paper']
            if pid not in seen_papers:
                seen_papers.add(pid)
                scores[pid] += 1 / (24 + len(seen_papers))
            prior = records.get(pid)
            hit = {k: d[k] for k in ('page','section','heading','text')} | {'query':term,'section_source':'heuristic'}
            if prior is None:
                records[pid] = {k: d[k] for k in ('paper','relpath','title','author','year','journal')} | {'hits':[hit]}
            elif len(prior['hits']) < 2 and all((x['page'],x['section']) != (d['page'],d['section']) for x in prior['hits']):
                prior['hits'].append(hit)
            if len(seen_papers) >= 32:
                break
        hit_counts[term] = len(seen_papers)
    return {'queries': hit_counts, 'papers': [records[k] | {'score':round(scores[k], 6)}
            for k in sorted(scores, key=lambda k: (-scores[k],k))[:limit]]}


def neighborhood(con, anchors, direction, depth, limit, include_tail):
    allowed = "" if include_tail else " AND l.method='section_title_author_year'"
    seen = set(anchors)
    frontier = list(dict.fromkeys(anchors))
    output = {}
    hit_cap = False
    for hop in range(1, depth + 1):
        future = []
        for anchor in frontier:
            sides = [('citing','cited')] if direction == 'past' else [('cited','citing')] if direction == 'future' else [('citing','cited'),('cited','citing')]
            for src, target in sides:
                for d in con.execute(f'''SELECT l.citing,l.cited,l.page,l.method,l.excerpt, n.id AS neighbor,
                    n.year,n.title,n.author,n.relpath,n.journal, c.relpath AS citing_pdf
                    FROM links l JOIN docs n ON n.id=l.{target} JOIN docs c ON c.id=l.citing
                    WHERE l.{src}=?{allowed} ORDER BY l.method, n.id LIMIT ?''', (anchor,limit+1)):
                    key = (d['citing'], d['cited'])
                    if key not in output:
                        if len(output) >= limit:
                            hit_cap = True
                            break
                        output[key] = dict(d) | {'anchor':anchor,'hop':hop,'relation':'citation_candidate'}
                    if d['neighbor'] not in seen:
                        seen.add(d['neighbor'])
                        future.append(d['neighbor'])
        frontier = future[:12]
        hit_cap |= len(future) > 12
        if not frontier or len(output) >= limit:
            break
    return {'anchors':anchors, 'direction':direction, 'edges':list(output.values()), 'bounded':hit_cap,
            'note':'citing → cited; exact normalized title + nearby filename author/year. Candidate citations, not model inheritance.'}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    commands = p.add_subparsers(dest='cmd', required=True)
    b = commands.add_parser('build')
    b.add_argument('--source', type=Path, default=paperlist.DEFAULT_DB)
    b.add_argument('--refresh', action='store_true', help='rescan in-corpus citation targets after papers are added')
    b.add_argument('--limit', type=paperlist.positive)
    commands.add_parser('status')
    s = commands.add_parser('search')
    s.add_argument('--term', action='append', default=[])
    s.add_argument('--phrase', action='append', default=[])
    s.add_argument('--journal', action='append', default=[])
    s.add_argument('--section', choices=SECTIONS)
    s.add_argument('--limit', type=paperlist.positive, default=10)
    c = commands.add_parser('citations')
    c.add_argument('paper', type=paperlist.positive, nargs='+')
    c.add_argument('--direction', choices=['past','future','both'], default='both')
    c.add_argument('--depth', type=int, choices=[1,2,3], default=1)
    c.add_argument('--limit', type=paperlist.positive, default=24)
    c.add_argument('--include-tail', action='store_true')
    return p


def main():
    paperlist.configure_output()
    args = parser().parse_args()
    try:
        if args.cmd == 'build':
            build(args)
        else:
            with closing(connect(args.db)) as con:
                if args.cmd == 'status':
                    result = stats(con)
                elif args.cmd == 'search':
                    result = passage_search(con,args.term,args.phrase,args.journal,args.section,min(args.limit,40))
                else:
                    result = neighborhood(con,args.paper[:12],args.direction,args.depth,min(args.limit,100),args.include_tail)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, ImportError, sqlite3.Error, OSError) as exc:
        print(f'corpus_rag: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
