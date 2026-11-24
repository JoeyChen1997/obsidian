"""Read-only evidence tools for the Paperlist research agent (no network or API key)."""

import argparse
from collections import Counter, defaultdict, deque
from contextlib import closing
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import sys
import unicodedata

import paperlist
import corpus_rag
import corpus_semantics
import citation_claims
import model_comparison


HERE = Path(__file__).resolve().parent
VAULT = HERE.parent
DEFAULT_GRAPH = HERE / 'research_graph.json'
EDGE_TYPES = {'introduces_component', 'extends_component', 'contrasts_assumptions',
              'limits_result', 'endogenizes', 'empirical_followup', 'cites'}
READ_STATES = {'core_read', 'screened', 'queued', 'source_gap'}
REVIEW_STATES = {'verified', 'screened', 'candidate'}
IDENTIFIER = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')
WORD = re.compile(r'[^\W_]+')
SECTIONS = {'introduction', 'model', 'results', 'discussion', 'proof', 'references'}


def norm(value):
    return ' '.join(WORD.findall(unicodedata.normalize('NFKC', value).casefold()))


def has_phrase(query, phrase):
    term = norm(phrase)
    if not term:
        return False
    if re.search(r'[\u3400-\u9fff]', term):
        return term in query
    return f' {term} ' in f' {query} '


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_items(items, label):
    result = {}
    for item in items:
        key = item['id']
        require(IDENTIFIER.fullmatch(key) and key not in result, f'Invalid or repeated {label} id: {key}')
        result[key] = item
    return result


def pdf_relpath(value):
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in value and ':' not in value
            and len(p.parts) >= 2 and p.suffix.lower() == '.pdf', f'Invalid paperlist path: {value}')


class Graph:
    def __init__(self, path):
        data = json.loads(path.read_text(encoding='utf-8'))
        require(data['schema_version'] == 1, 'Unsupported research graph schema.')
        self.papers = unique_items(data['papers'], 'paper')
        self.topics = unique_items(data['topics'], 'topic')
        self.edges = unique_items(data['edges'], 'edge')
        self.source_exclusions = {}
        self.adjacent = defaultdict(list)
        files = set()
        for key, paper in self.papers.items():
            require(paper['reading_status'] in READ_STATES, f'Invalid paper status: {key}')
            require(type(paper['year']) is int and 1700 <= paper['year'] <= 2200, f'Invalid year: {key}')
            if source := paper.get('pdf'):
                pdf_relpath(source)
                require(source.casefold() not in files, f'Duplicate PDF path: {source}')
                files.add(source.casefold())
            for variant in paper.get('verified_variants', []):
                pdf = variant['pdf']
                pdf_relpath(pdf)
                require(pdf.casefold() not in files, f'Duplicate PDF path: {pdf}')
                files.add(pdf.casefold())
                require(variant['kind'] in {'reprint', 'working_paper', 'supplement', 'same_edition_copy'},
                        f'Invalid source role: {key}')
                require(type(variant['identity_page']) is int and variant['identity_page'] >= 1
                        and isinstance(variant['identity_note'], str) and variant['identity_note'].strip(),
                        f'Variant lacks identity evidence: {key}')
            if paper.get('card'):
                card = (VAULT / paper['card']).resolve()
                require(card.is_relative_to(VAULT) and card.suffix == '.md', f'Invalid card path: {key}')
            for section, ranges in paper.get('sections', {}).items():
                require(section in SECTIONS and bool(ranges), f'Invalid section: {key}/{section}')
                for start, end in ranges:
                    require(type(start) is int and type(end) is int and 1 <= start <= end,
                            f'Invalid section range: {key}/{section}')
        for item in data.get('source_exclusions', []):
            source_id, pdf = item['source_id'], item['pdf']
            pdf_relpath(pdf)
            require(type(source_id) is int and source_id > 0 and source_id not in self.source_exclusions
                    and pdf.casefold() not in files, f'Duplicate or invalid excluded source: {pdf}')
            require(item['kind'] == 'volume_index' and type(item['page']) is int and item['page'] > 0
                    and isinstance(item.get('locator'), str) and item['locator'].strip(),
                    f'Excluded source needs original page evidence: {pdf}')
            files.add(pdf.casefold())
            self.source_exclusions[source_id] = item
        for key, topic in self.topics.items():
            require(topic['papers'] and set(topic['papers']) <= self.papers.keys(), f'Invalid topic papers: {key}')
            require(topic['queries'] and all(isinstance(q, str) and norm(q) for q in topic['queries']),
                    f'Invalid topic queries: {key}')
        for key, edge in self.edges.items():
            old, new = edge['from'], edge['to']
            require(old in self.papers and new in self.papers and old != new, f'Invalid endpoints: {key}')
            require(self.papers[old]['year'] <= self.papers[new]['year'], f'Reversed timeline: {key}')
            require(edge['type'] in EDGE_TYPES and edge['review'] in REVIEW_STATES, f'Invalid edge type or state: {key}')
            require(all(isinstance(edge.get(k), str) and edge[k].strip() for k in ('claim', 'changed', 'limit')),
                    f'Missing claim, change, or limit: {key}')
            require(edge['review'] == 'candidate' or bool(edge['evidence']), f'Evidence required for {key}')
            for ev in edge['evidence']:
                source = ev['paper']
                require(source in self.papers and bool(self.papers[source].get('pdf')), f'Missing PDF for {key}')
                require(type(ev['page']) is int and ev['page'] > 0 and bool(ev['locator'].strip()),
                        f'Invalid page evidence: {key}')
            self.adjacent[old].append(key)
            self.adjacent[new].append(key)
        for key in self.adjacent:
            self.adjacent[key].sort()

    def node(self, key):
        result = dict(self.papers[key])
        if result.get('card') and not (VAULT / result['card']).is_file():
            result['card_available'] = False
        elif result.get('card'):
            result['card_available'] = True
        return result

    def anchors(self, question, explicit):
        question = norm(question)
        selected, topics = set(), []
        for key in explicit:
            require(key in self.topics or key in self.papers, f'Unknown graph id: {key}')
            if key in self.topics:
                topics.append(key)
            else:
                selected.add(key)
        if not explicit:
            for key, paper in self.papers.items():
                if any(has_phrase(question, alias) for alias in [key, paper['title'], *paper.get('aliases', [])]):
                    selected.add(key)
            for key, topic in self.topics.items():
                if any(has_phrase(question, a) for a in [key, topic['title'], *topic.get('aliases', [])]):
                    topics.append(key)
        for key in topics:
            selected.update(self.topics[key]['papers'])
        return sorted(selected, key=lambda k: (self.papers[k]['year'], k)), list(dict.fromkeys(topics))

    def trace(self, anchors, depth, direction):
        todo = deque((k, 0) for k in anchors)
        seen = set(anchors)
        edges = set()
        while todo:
            key, hops = todo.popleft()
            if hops >= depth:
                continue
            for edge_id in self.adjacent[key]:
                edge = self.edges[edge_id]
                old, new = edge['from'], edge['to']
                if (direction == 'past' and key == old) or (direction == 'future' and key == new):
                    continue
                edges.add(edge_id)
                other = new if key == old else old
                # Do not use provisional or mere citation edges to infer additional links.
                if edge['review'] == 'verified' and edge['type'] != 'cites' and other not in seen:
                    seen.add(other)
                    todo.append((other, hops + 1))
        ordered = sorted((self.edges[k] for k in edges),
                         key=lambda e: (self.papers[e['to']]['year'], self.papers[e['from']]['year'], e['id']))
        nodes = set(anchors) | {e[endpoint] for e in ordered for endpoint in ('from', 'to')}
        return {'anchors': anchors,
                'papers': [self.node(k) for k in sorted(nodes, key=lambda k: (self.papers[k]['year'], k))],
                'relations': [self.expand_edge(e) for e in ordered if e['review'] == 'verified' and e['type'] != 'cites'],
                'leads': [self.expand_edge(e) for e in ordered if e['review'] != 'verified' or e['type'] == 'cites']}

    def expand_edge(self, edge):
        return edge | {'year': self.papers[edge['to']]['year'],
                       'evidence': [ev | {'pdf': self.papers[ev['paper']]['pdf']} for ev in edge['evidence']]}

    def paths(self, older, later, depth, include_screened):
        require(older in self.papers and later in self.papers and older != later,
                'Path requires two distinct graph paper IDs.')
        require(self.papers[older]['year'] <= self.papers[later]['year'], 'Supply the older paper first.')
        allowed = {'verified', 'screened'} if include_screened else {'verified'}
        paths = []
        todo = deque([(older, (older,), ())])
        allocated, truncated = 1, False
        while todo and len(paths) < 12:
            key, nodes, chain = todo.popleft()
            if key == later:
                paths.append({'papers': [self.node(p) for p in nodes],
                              'relations': [self.expand_edge(e) for e in chain],
                              'contains_screened_edge': any(e['review'] == 'screened' for e in chain)})
                continue
            if len(chain) == depth:
                continue
            for edge_id in self.adjacent[key]:
                edge = self.edges[edge_id]
                nxt = edge['to']
                if (edge['from'] == key and nxt not in nodes and edge['type'] != 'cites' and edge['review'] in allowed
                        and self.papers[nxt]['year'] <= self.papers[later]['year']):
                    if allocated < 3000:
                        todo.append((nxt, (*nodes, nxt), (*chain, edge)))
                        allocated += 1
                    else:
                        truncated = True
        return {'from': older, 'to': later, 'paths': paths, 'include_screened': include_screened,
                'truncated': bool(todo) or truncated,
                'note': 'No path means no recorded chain within these limits, not no relationship. A path is not a causal proof.'}

    def validate_sources(self, con):
        required = defaultdict(set)
        for edge in self.edges.values():
            for ev in edge['evidence']:
                required[ev['paper']].add(ev['page'])
        missing_cards = []
        variant_pages_checked = 0
        for key, paper in self.papers.items():
            if paper.get('card') and not self.node(key)['card_available']:
                missing_cards.append(key)
            if pdf := paper.get('pdf'):
                source = con.execute("SELECT id, pages FROM papers WHERE relpath=? AND status <> 'missing'", (pdf,)).fetchone()
                require(source is not None, f'PDF not in catalog: {key}: {pdf}')
                declared = [end for ranges in paper.get('sections', {}).values() for _, end in ranges]
                for page in sorted(set(declared) | required[key]):
                    require(source['pages'] and page <= source['pages'], f'Page {page} is outside {key}')
                for page in sorted(required[key]):
                    require(con.execute('SELECT 1 FROM page_index WHERE rowid=?',
                                        (source['id'] * paperlist.PAGE_STRIDE + page,)).fetchone() is not None,
                            f'No searchable text for evidence page {key}:{page}')
            for variant in paper.get('verified_variants', []):
                source = con.execute("SELECT id,pages FROM papers WHERE relpath=? AND status <> 'missing'",
                                     (variant['pdf'],)).fetchone()
                page = variant['identity_page']
                require(source is not None and source['pages'] and page <= source['pages'],
                        f"Missing or invalid identity source: {variant['pdf']}")
                require(con.execute('SELECT 1 FROM page_index WHERE rowid=?',
                                    (source['id'] * paperlist.PAGE_STRIDE + page,)).fetchone() is not None,
                        f"No indexed identity page: {variant['pdf']}:{page}")
                variant_pages_checked += 1
        for source_id, item in self.source_exclusions.items():
            source = con.execute('SELECT relpath,pages,status FROM papers WHERE id=?', (source_id,)).fetchone()
            require(source is not None and source['relpath'] == item['pdf'] and source['pages']
                    and item['page'] <= source['pages'], f"Invalid exclusion source: {item['pdf']}")
            if source['status'] != 'missing':
                require(con.execute('SELECT 1 FROM page_index WHERE rowid=?',
                                    (source_id * paperlist.PAGE_STRIDE + item['page'],)).fetchone() is not None,
                        f"No indexed exclusion proof page: {item['pdf']}:{item['page']}")
        return {'papers': len(self.papers), 'topics': len(self.topics), 'edges': len(self.edges),
                'reading_states': dict(Counter(p['reading_status'] for p in self.papers.values())),
                'edge_review_states': dict(Counter(e['review'] for e in self.edges.values())),
                'evidence_pages_checked': sum(len(pages) for pages in required.values()),
                'variant_identity_pages_checked': variant_pages_checked,
                'source_exclusion_records_checked': len(self.source_exclusions),
                'missing_markdown_cards': missing_cards}


def quote_query(query, phrase):
    words = WORD.findall(unicodedata.normalize('NFKC', query))
    if not words:
        return None
    return '"' + ' '.join(words) + '"' if phrase else ' AND '.join(f'"{w}"' for w in words)


def retrieve(con, terms, args):
    clauses = ["p.status <> 'missing'"]
    filters = []
    if args.journal:
        clauses.append(f"upper(p.journal) IN ({','.join('?' for _ in args.journal)})")
        filters.extend(v.upper() for v in args.journal)
    for field, op in [('from_year', '>='), ('to_year', '<=')]:
        value = getattr(args, field)
        if value is not None:
            clauses.append(f'p.year {op} ?')
            filters.append(value)
    where = ' AND '.join(clauses)
    info = 'p.id, p.relpath, p.title_hint, p.author_hint, p.year AS filename_year, p.journal, p.status'
    scores = defaultdict(float)
    papers = {}
    audit = []
    root = paperlist.get_root(con)
    for term in terms:
        phrase = term in args.phrase
        match = quote_query(term, phrase)
        if not match:
            continue
        counts = {}
        for channel, weight, sql in [
            ('catalog', 1.25, f'''SELECT {info} FROM catalog JOIN papers p ON p.id=catalog.rowid
              WHERE catalog MATCH ? AND {where} ORDER BY rank LIMIT 24'''),
            ('page', 1.0, f'''SELECT {info}, page_index.pdf_page,
              CASE WHEN o.result='text' THEN 'ocr' ELSE 'pdf_text' END AS text_source,
              snippet(page_index,2,'[',']',' … ',28) AS excerpt
              FROM page_index JOIN papers p ON p.id=page_index.paper_id
              LEFT JOIN ocr_attempts o ON o.rowid=page_index.rowid
              WHERE page_index MATCH ? AND {where} ORDER BY rank LIMIT 140''')]:
            seen = set()
            for hit in con.execute(sql, [match, *filters]):
                row = dict(hit)
                key = row['id']
                if key not in papers:
                    papers[key] = {k: row[k] for k in ('id', 'relpath', 'title_hint', 'author_hint', 'filename_year', 'journal', 'status')}
                    papers[key].update(pdf=str(root / row['relpath']), title_queries=[], pages=[])
                p = papers[key]
                if key not in seen:
                    seen.add(key)
                    scores[key] += weight / (24 + len(seen))
                    if channel == 'catalog':
                        p['title_queries'].append(term)
                if channel == 'page' and len(p['pages']) < 3 and all(x['pdf_page'] != row['pdf_page'] for x in p['pages']):
                    p['pages'].append({k: row[k] for k in ('pdf_page', 'text_source', 'excerpt')} | {'query': term})
                if len(seen) >= 24:
                    break
            counts[channel] = len(seen)
        audit.append({'query': term, 'match': 'phrase' if phrase else 'all_terms_within_one_page',
                      'sampled_papers': counts})
    selected = sorted(papers, key=lambda key: (-scores[key], key))[:args.limit]
    return {'queries': audit, 'filters': {'journals': args.journal, 'from_filename_year': args.from_year,
                                         'to_filename_year': args.to_year},
            'ranking': 'title/author and page BM25; reciprocal rank fusion across queries; candidate only',
            'papers': [papers[k] | {'rank_score': round(scores[k], 5)} for k in selected]}


def corpus_layer(source, args, traced, lexical, terms, source_exclusions):
    path = args.corpus_db
    if path is None and args.db.resolve() == paperlist.DEFAULT_DB.resolve():
        path = corpus_rag.DEFAULT_DB
    if not path or not path.is_file():
        return {'available':False,'note':'Section/citation index not available for this catalog; used original page search.'}
    with closing(corpus_rag.connect(path)) as pre:
        pre.execute('BEGIN')
        bound = pre.execute("SELECT value FROM config WHERE key='source'").fetchone()
        require(bound is not None and Path(bound[0]).resolve() == args.db.resolve(), 'RAG index belongs to another catalog.')
        passages = corpus_rag.passage_search(pre,terms,args.phrase,args.journal,args.section,args.limit,
                                             args.from_year,args.to_year)
        for paper in passages['papers']:
            for hit in paper['hits']:
                ocr = source.execute("SELECT result FROM ocr_attempts WHERE rowid=?",
                                     (paper['paper']*paperlist.PAGE_STRIDE+hit['page'],)).fetchone()
                hit['text_source'] = 'ocr' if ocr and ocr[0]=='text' else 'pdf_text'
        dense = {'papers':[], 'state':'not_requested'}
        if args.semantic:
            import corpus_vectors

            try:
                dense = corpus_vectors.search(pre,path,args.vector_db or corpus_vectors.DEFAULT_DB,list(dict.fromkeys(args.semantic))[:8],
                                              args.journal,args.limit,args.from_year,args.to_year) | {'state':'available'}
            except (ValueError,ImportError,OSError,sqlite3.Error) as err:
                dense = {'papers':[],'state':'unavailable','note':str(err)}
        ranks = defaultdict(float)
        channels = defaultdict(list)
        for name, weight, results, key in [('title_page',1,lexical['papers'],'id'),
                ('section_passages',1.3,passages['papers'],'paper'),('dense_document',0.9,dense['papers'],'id')]:
            for rank, hit in enumerate(results,1):
                paper = hit[key]
                ranks[paper] += weight / (20+rank)
                channels[paper].append(name)
        exclusions = {}
        for source_id, item in source_exclusions.items():
            row = source.execute('SELECT relpath FROM papers WHERE id=?', (source_id,)).fetchone()
            if row and row['relpath'] == item['pdf']:
                exclusions[source_id] = item
        excluded_hits = []
        shortlist = []
        for paper in sorted(ranks,key=lambda k:(-ranks[k],k)):
            row = source.execute('SELECT id,relpath,title_hint,author_hint,year,journal FROM papers WHERE id=?',(paper,)).fetchone()
            if row:
                hit = dict(row) | {'channels': channels[paper], 'score': round(ranks[paper], 6)}
                if paper in exclusions:
                    excluded_hits.append(hit | {'source_exclusion': exclusions[paper]})
                elif len(shortlist) < args.limit:
                    shortlist.append(hit)
        anchors = []
        for node in traced['papers']:
            if node['id'] in traced['anchors'] and node.get('pdf'):
                item = pre.execute('SELECT id FROM docs WHERE relpath=?',(node['pdf'],)).fetchone()
                if item:
                    anchors.append(item['id'])
        anchors = list(dict.fromkeys(p for p in [*anchors, *args.citation_seed, *[h['id'] for h in shortlist[:3]]]
                                     if p not in exclusions))[:8]
        if args.intent in ('lineage','compare','write') or args.citation_seed:
            citations = {side:corpus_rag.neighborhood(pre,anchors,side,min(args.depth,3),args.citation_limit,args.include_tail)
                         for side in ('past','future') if args.direction in (side,'both') and anchors}
        else:
            citations = {}
        comparison = {'pairs': [], 'note': 'Use lineage or compare intent to expand model-assumption comparisons.'}
        if args.intent in ('lineage', 'compare'):
            comparison = model_comparison.compare(pre,
                [*anchors, *[p['id'] for p in shortlist]], [*terms, *args.semantic],
                args.journal, args.from_year, args.to_year, min(args.limit, 8))
        semantic_graph = {'available': False, 'note': 'Build the local semantic index with corpus_semantics.py build.'}
        semantic_path = args.semantic_db
        if semantic_path is None and args.db.resolve() == paperlist.DEFAULT_DB.resolve():
            semantic_path = corpus_semantics.DEFAULT_DB
        if semantic_path and semantic_path.is_file():
            try:
                with closing(corpus_semantics.connect(semantic_path)) as semantic:
                    semantic.execute('BEGIN')
                    bound = corpus_semantics.check_bindings(semantic, pre, path, args.db)
                    semantic_graph = corpus_semantics.contextualize(
                        semantic, pre, bound, list(dict.fromkeys([*terms, *args.semantic])),
                        anchors, args.direction, min(args.depth, 3), min(args.citation_limit, 24))
                    semantic_graph['available'] = True
            except (ValueError, ImportError, OSError, sqlite3.Error) as err:
                semantic_graph = {'available': False, 'note': str(err)}
        attribution_graph = {'available': False, 'note': 'Use lineage, compare, or write with a built citation_claims index.'}
        attribution_path = args.claims_db
        if attribution_path is None and args.db.resolve() == paperlist.DEFAULT_DB.resolve():
            attribution_path = citation_claims.DEFAULT_DB
        if args.intent in ('lineage', 'compare', 'write') and attribution_path and attribution_path.is_file():
            try:
                with closing(citation_claims.connect(attribution_path)) as claims:
                    claims.execute('BEGIN')
                    citation_claims.check_binding(claims, pre, path)
                    attribution_graph = citation_claims.search(
                        claims, pre, [*anchors, *[p['id'] for p in shortlist[:6]]],
                        [*terms, *args.semantic], args.direction, min(args.citation_limit, 18))
                    attribution_graph['corpus_pdfs'] = pre.execute('SELECT COUNT(*) FROM docs').fetchone()[0]
            except (ValueError, OSError, sqlite3.Error) as err:
                attribution_graph = {'available': False, 'note': str(err)}
        coverage = dict(pre.execute('SELECT COUNT(*) AS documents,SUM(page_count) AS source_pages, SUM(page_count=0) AS no_text FROM docs').fetchone())
        return {'available':True,'coverage':coverage,'ranked_candidates':shortlist,
                'excluded_nonresearch_hits':excluded_hits,'passages':passages,
                'dense':dense,'citation_candidates':citations,'semantic_graph':semantic_graph,
                'model_comparison_leads':comparison,'citation_attributions':attribution_graph,
                'notes':['Section labels and citation matches are machine-generated leads, not independently checked facts.',
                         'Use corpus_rag.py context to locate actual discussion before upgrading a citation to a model relation.']}


def evidence(graph, con, args):
    if args.paper in graph.papers:
        paper = graph.node(args.paper)
        require(bool(paper.get('pdf')), f'No local PDF registered for {args.paper}')
        source = con.execute("SELECT * FROM papers WHERE relpath=? AND status <> 'missing'", (paper['pdf'],)).fetchone()
    else:
        require(args.paper.isdecimal() and 0 < int(args.paper) < 2**63, f'Unknown paper id: {args.paper}')
        paper = None
        source = con.execute("SELECT * FROM papers WHERE id=? AND status <> 'missing'", (int(args.paper),)).fetchone()
    require(source is not None, f'PDF is not in the catalog: {args.paper}')
    require(bool(source['pages']), f'Page count not available for {args.paper}')
    pages = list(args.page)
    if args.section:
        ranges = paper.get('sections', {}).get(args.section) if paper else None
        require(bool(ranges), f'No verified {args.section} page map for {args.paper}; specify --page or inspect the original PDF.')
        if not pages:
            pages = [n for lo, hi in ranges for n in range(lo, hi + 1)]
        else:
            require(all(any(lo <= n <= hi for lo, hi in ranges) for n in pages), 'Requested page is outside the mapped section.')
    pages = list(dict.fromkeys(pages))
    require(bool(pages), 'Select --page (repeatable) or --section.')
    require(all(0 < n <= source['pages'] for n in pages), f"PDF has {source['pages']} physical pages.")
    result = []
    for number in pages[:args.limit]:
        row = con.execute('''SELECT body, CASE WHEN o.result='text' THEN 'ocr' ELSE 'pdf_text' END AS text_source
             FROM page_index LEFT JOIN ocr_attempts o ON o.rowid=page_index.rowid WHERE page_index.rowid=?''',
             (source['id'] * paperlist.PAGE_STRIDE + number,)).fetchone()
        result.append({'pdf_page': number, 'text_source': row['text_source'] if row else None,
                       'indexed_text': row['body'][:args.chars] if row else None,
                       'truncated': bool(row and len(row['body']) > args.chars)})
    return {'paper': paper or {'id': source['id'], 'title_hint': source['title_hint']},
            'pdf': str(paperlist.get_root(con) / source['relpath']), 'section': args.section,
            'page_limit_applied': len(pages) > args.limit, 'pages': result,
            'note': 'Physical PDF pages, starting at 1. Verify equations, quotes and printed pages in the original.'}


def bounded(maximum):
    def parse(value):
        number = int(value)
        if not 1 <= number <= maximum:
            raise argparse.ArgumentTypeError(f'must be between 1 and {maximum}')
        return number
    return parse


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=paperlist.DEFAULT_DB)
    p.add_argument('--graph', type=Path, default=DEFAULT_GRAPH)
    p.add_argument('--corpus-db',type=Path,help='separate full-corpus sections and citation database')
    p.add_argument('--vector-db',type=Path,help='separate local dense index')
    p.add_argument('--semantic-db',type=Path,help='separate local semantic candidate graph')
    p.add_argument('--claims-db',type=Path,help='separate local citation attribution index')
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('validate', help='verify graph schema and evidence pages against the local catalog')
    sub.add_parser('topics', help='list available graph topics and paper IDs')
    path = sub.add_parser('path', help='find evidence-backed directed chains between two graph papers')
    path.add_argument('older')
    path.add_argument('later')
    path.add_argument('--depth', type=bounded(4), default=3)
    path.add_argument('--include-screened', action='store_true')
    for command in ('trace', 'brief'):
        q = sub.add_parser(command, help='trace reviewed relations' if command == 'trace' else 'assemble a research evidence packet')
        q.add_argument('question', nargs='?', default='')
        q.add_argument('--anchor', action='append', default=[], help='topic or paper ID; repeat to select multiple')
        q.add_argument('--depth', type=bounded(4), default=2)
        q.add_argument('--direction', choices=['past', 'future', 'both'], default='both')
        if command == 'brief':
            q.add_argument('--intent', choices=['discover', 'lineage', 'compare', 'write'], default='discover')
            q.add_argument('--term', action='append', default=[], help='all words must match; repeat with English synonyms')
            q.add_argument('--phrase', action='append', default=[], help='exact token phrase; repeatable')
            q.add_argument('--journal', action='append', default=[])
            q.add_argument('--from-year', type=int)
            q.add_argument('--to-year', type=int)
            q.add_argument('--limit', type=bounded(30), default=10)
            q.add_argument('--semantic',action='append',default=[],help='English natural-language dense query (repeatable)')
            q.add_argument('--section',choices=corpus_rag.SECTIONS,help='restrict the passage search channel only')
            q.add_argument('--citation-seed',action='append',type=bounded(99_999_999),default=[])
            q.add_argument('--citation-limit',type=bounded(100),default=16)
            q.add_argument('--include-tail',action='store_true',help='allow low-confidence matches outside detected references')
    q = sub.add_parser('evidence', help='fetch text for explicit PDF pages or verified sections')
    q.add_argument('paper', help='graph paper ID or numeric paperlist ID')
    q.add_argument('--page', action='append', type=bounded(999999), default=[])
    q.add_argument('--section', choices=sorted(SECTIONS))
    q.add_argument('--limit', type=bounded(10), default=4)
    q.add_argument('--chars', type=bounded(18000), default=7500)
    return p


def run(args, graph):
    if args.cmd == 'topics':
        return {'topics': list(graph.topics.values()), 'paper_ids': list(graph.papers)}
    if args.cmd == 'path':
        return graph.paths(args.older, args.later, args.depth, args.include_screened)
    if args.cmd in ('trace', 'brief'):
        anchors, topics = graph.anchors(args.question, args.anchor)
        traced = graph.trace(anchors, args.depth, args.direction)
        traced['topics'] = topics
        if args.cmd == 'trace':
            return traced
    with closing(paperlist.connect(args.db)) as con:
        if args.cmd == 'validate':
            return graph.validate_sources(con)
        if args.cmd == 'evidence':
            return evidence(graph, con, args)
        require(args.from_year is None or args.to_year is None or args.from_year <= args.to_year,
                '--from-year must not exceed --to-year')
        terms = list(dict.fromkeys([*args.term, *args.phrase]))
        if not terms:
            terms = list(dict.fromkeys(term for t in topics for term in graph.topics[t]['queries']))[:8]
            if not terms:
                # Graph anchors can seed a bibliography pass even when a topic has not been tagged.
                args.phrase = list(dict.fromkeys(graph.papers[key]['title'] for key in anchors))[:4]
                terms = args.phrase
        require(len(terms) <= 8, 'Supply at most eight distinct retrieval queries per brief.')
        require(all(quote_query(t, t in args.phrase) for t in terms), 'Search terms must include a letter or number.')
        require(len(args.semantic) <= 8 and all(norm(t) for t in args.semantic),
                'Supply up to eight nonempty semantic queries.')
        coverage = dict(con.execute('''SELECT COUNT(*) AS pdf_files, SUM(text_pages) AS searchable_pages,
            SUM(status='pending') AS pending, SUM(status IN ('partial','no_text','error')) AS text_gaps
            FROM papers WHERE status <> 'missing' ''').fetchone())
        lexical = retrieve(con, terms, args)
        return {'question': args.question, 'intent': args.intent, 'coverage': coverage,
                'graph': traced, 'retrieval': lexical,
                'corpus_rag':corpus_layer(con,args,traced,lexical,terms,graph.source_exclusions),
                'notes': ['Graph coverage is curated and incomplete; graph edges are not causal proof.',
                          'Journal/year filters apply to search, not historical graph neighbors. Search years come from filenames.',
                          'Semantic matches and automated citations supplement lexical evidence; no external citation database.',
                          *([] if terms else ['No lexical search was run; pass --term or --phrase with 2-6 focused English queries.'])]}


def main():
    paperlist.configure_output()
    args = parser().parse_args()
    try:
        result = run(args, Graph(args.graph))
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError, OverflowError) as exc:
        print(f'research_agent: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
