"""Read-only full-corpus coverage rollup and paginated review queue."""

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import json
from pathlib import Path

import corpus_rag
import paperlist
from research_agent import DEFAULT_GRAPH, Graph


def coverage(con, graph):
    catalog = con.execute('''SELECT id,relpath,journal,year,title_hint,author_hint,status,pages,text_pages
                             FROM papers ORDER BY id''').fetchall()
    by_pdf = {node['pdf'].replace('\\', '/').casefold(): key for key, node in graph.papers.items() if node.get('pdf')}
    title_groups = defaultdict(list)
    source_rows = []
    registered = set()
    for source in catalog:
        row = dict(source)
        key = by_pdf.get(row['relpath'].replace('\\', '/').casefold())
        node = graph.node(key) if key else {}
        state = node.get('reading_status', 'not_reviewed')
        if key:
            registered.add(key)
        title = corpus_rag.normalized_title(row['title_hint'] or '')
        if row['status'] != 'missing' and len(title) >= 16 and len(title.split()) >= 3:
            title_groups[title].append(row['id'])
        pages, text = row['pages'], row['text_pages']
        source_issue = (
            'missing' if row['status'] == 'missing' else
            'pending' if row['status'] == 'pending' else
            'no_indexed_text' if not text else
            'partial_indexed_text' if pages and text < pages else None
        )
        row.update(work_id=key, identity_state='registered_work' if key else 'unresolved',
                   reading_state=state, source_issue=source_issue, doi=node.get('doi'),
                   publication_year=node.get('year'), reading_note=node.get('reading_note'),
                   card=node.get('card'), card_available=node.get('card_available'))
        source_rows.append(row)
    # Candidate families are for manual adjudication; not mergers or duplicate counts.
    groups = {i: members for i, members in enumerate(
        (g for g in title_groups.values() if len(g) > 1), start=1)}
    candidate_by_id = {key: i for i, members in groups.items() for key in members}
    for row in source_rows:
        row['same_title_candidate_group'] = candidate_by_id.get(row['id'])
    live = [x for x in source_rows if x['status'] != 'missing']
    summary = {
        'catalog_records': len(source_rows),
        'present_pdf_records': len(live),
        'catalog_missing_pdf_records': len(source_rows) - len(live),
        'present_by_journal': dict(Counter(x['journal'] for x in live)),
        'present_by_reading_state': dict(Counter(x['reading_state'] for x in live)),
        'present_source_issues': dict(Counter(x['source_issue'] for x in live if x['source_issue'])),
        'registered_graph_works': len(graph.papers),
        'present_registered_work_ids': len({x['work_id'] for x in live if x['work_id']}),
        'present_unresolved_pdf_identities': sum(x['work_id'] is None for x in live),
        'same_title_candidate_groups': len(groups),
        'pdfs_in_same_title_candidate_groups': len(candidate_by_id),
        'graph_nodes_without_catalog_source': [
            {'id': key, 'title': node['title'], 'reading_state': node['reading_status']}
            for key, node in graph.papers.items() if key not in registered],
        'unavailable_registered_cards': [
            x['work_id'] for x in source_rows if x['card'] and not x['card_available']],
        'note': 'Present is the last catalog observation, not a fresh filesystem walk. Same-title groups are '
                'candidates only; independent-work count for the corpus is not yet established.'
    }
    return summary, source_rows, groups


def main():
    paperlist.configure_output()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=paperlist.DEFAULT_DB)
    p.add_argument('--graph', type=Path, default=DEFAULT_GRAPH)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    q = sub.add_parser('queue')
    q.add_argument('--journal')
    q.add_argument('--state', choices=['not_reviewed', 'queued', 'screened', 'core_read', 'source_gap'])
    q.add_argument('--issues-only', action='store_true')
    q.add_argument('--after', type=int, default=0)
    q.add_argument('--limit', type=int, default=20)
    q = sub.add_parser('versions')
    q.add_argument('source_id', type=int)
    args = p.parse_args()
    with closing(paperlist.connect(args.db)) as con:
        summary, rows, groups = coverage(con, Graph(args.graph))
    if args.command == 'status':
        result = summary
    elif args.command == 'queue':
        if not 1 <= args.limit <= 200 or args.after < 0:
            p.error('limit must be 1–200 and after must be non-negative')
        eligible = [r for r in rows if r['id'] > args.after and
                    (not args.journal or args.journal.upper() == r['journal'].upper()) and
                    (not args.state or args.state == r['reading_state']) and
                    (not args.issues_only or r['source_issue'])]
        selected = eligible[:args.limit]
        result = {'sources': selected, 'next_after': selected[-1]['id'] if len(eligible) > len(selected) else None}
    else:
        source = next((r for r in rows if r['id'] == args.source_id), None)
        if source is None:
            p.error('source ID not in catalog')
        ids = set(groups.get(source['same_title_candidate_group'], []))
        result = {'source': source, 'exact_normalized_title_candidates': [
            r for r in rows if r['id'] != args.source_id and r['id'] in ids],
            'note': 'Check DOI, author and publication page before joining versions; other versions may be missing.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
