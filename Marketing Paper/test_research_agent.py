"""Offline regression tests using a miniature FTS5 index and the bundled graph."""

import json
from pathlib import Path
import tempfile
import unittest

import paperlist
from research_agent import DEFAULT_GRAPH, Graph, parser, run


class ResearchAgentTest(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(DEFAULT_GRAPH)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        base = Path(self.directory.name)
        self.db = base / 'test.sqlite3'
        con = paperlist.connect(self.db, writable=True)
        try:
            con.execute("INSERT INTO settings VALUES ('root', ?)", (str(base),))
            for paper_id, journal, year, title, body in (
                (1, 'MKSC', 2018, 'Agency Selling and Platforms', 'We compare agency selling with wholesale pricing.'),
                (2, 'MS', 2024, 'Reselling and Revenue Sharing', 'The platform chooses revenue sharing or agency selling.'),
                (3, 'AER', 2010, 'An Unrelated Platform', 'An agency funds its domestic platform without selling any products.'),
            ):
                relpath = f'{journal}/{title}.pdf'
                con.execute('''INSERT INTO papers(id,relpath,journal,author_hint,year,title_hint,
                    size,mtime_ns,status,pages,text_pages) VALUES (?,?,?,?,?,?,1,1,'indexed',8,1)''',
                            (paper_id, relpath, journal, 'Test Author', year, title))
                con.execute('INSERT INTO catalog(rowid,title,author) VALUES (?,?,?)', (paper_id, title, 'Test Author'))
                con.execute('INSERT INTO page_index(rowid,paper_id,pdf_page,body) VALUES (?,?,?,?)',
                            (paper_id * paperlist.PAGE_STRIDE + 4, paper_id, 4, body))
            con.execute("INSERT INTO ocr_attempts VALUES (?, 'text', NULL)", (paperlist.PAGE_STRIDE + 4,))
            con.commit()
        finally:
            con.close()

    def run_tool(self, *args):
        return run(parser().parse_args(['--db', str(self.db), *args]), self.graph)

    def test_chinese_topic_preserves_review_boundaries(self):
        result = self.run_tool('trace', '想知道定向广告和定向定价的历史')
        self.assertEqual(result['topics'], ['targeting'])
        self.assertIn('iyer-moorthy-conditional-profit', {e['id'] for e in result['relations']})
        self.assertIn('moorthy-zhu-endogenous-rates', {e['id'] for e in result['relations']})
        self.assertNotIn('cites', {e['type'] for e in result['relations']})

    def test_directed_path_excludes_unreviewed_by_default(self):
        base = self.run_tool('path', 'butters-1977', 'moorthy-2023')
        self.assertEqual(base['paths'], [])
        expanded = self.run_tool('path', 'butters-1977', 'moorthy-2023', '--include-screened')
        self.assertEqual(len(expanded['paths']), 1)
        path = expanded['paths'][0]
        self.assertEqual([p['id'] for p in path['papers']], ['butters-1977', 'grossman-1984', 'moorthy-2023'])
        self.assertTrue(path['contains_screened_edge'])
        with self.assertRaisesRegex(ValueError, 'older paper'):
            self.run_tool('path', 'zhu-2025', 'iyer-2005')

    def test_reviewed_channel_chain_has_bilateral_evidence_and_limits(self):
        result = self.run_tool('trace', '分销渠道与产品质量')
        self.assertEqual(result['topics'], ['channel-quality'])
        path, = self.run_tool('path', 'jeuland-shugan-1983', 'shi-liu-petruzzi-2013')['paths']
        self.assertEqual([p['id'] for p in path['papers']],
                         ['jeuland-shugan-1983', 'xu-2009', 'shi-liu-petruzzi-2013'])
        for edge in path['relations']:
            self.assertEqual({e['paper'] for e in edge['evidence']}, {edge['from'], edge['to']})
        self.assertFalse(path['contains_screened_edge'])

    def test_verified_privacy_path_distinguishes_model_change_and_welfare(self):
        result = self.run_tool('path', 'iyer-2005', 'zhu-2025')
        path, = result['paths']
        self.assertFalse(path['contains_screened_edge'])
        edge = path['relations'][-1]
        self.assertEqual(edge['id'], 'moorthy-zhu-endogenous-rates')
        self.assertTrue({9, 11}.issubset({e['page'] for e in edge['evidence'] if e['paper']=='zhu-2025'}))

    def test_past_does_not_return_future_papers(self):
        result = self.run_tool('trace', '--anchor', 'moorthy-2023', '--direction', 'past')
        self.assertNotIn('zhu-2025', {p['id'] for p in result['papers']})
        self.assertTrue(all(p['year'] <= 2023 for p in result['papers']))

    def test_search_empirical_followup_uses_verified_years(self):
        result = self.run_tool('trace', '平台搜索精度')
        self.assertIn('platform-search-precision', result['topics'])
        edge, = [e for e in result['relations'] if e['id'] == 'zhong-zhou-search-precision-followup']
        self.assertEqual(edge['type'], 'empirical_followup')
        years = {p['id']: p['year'] for p in result['papers']}
        self.assertEqual((years[edge['from']], years[edge['to']]), (2023, 2025))
        self.assertEqual({e['paper'] for e in edge['evidence']}, {edge['from'], edge['to']})

    def test_unknown_topic_uses_fts_with_phrase_and_filters(self):
        result = self.run_tool('brief', '卖家为什么采用代理模式', '--phrase', 'agency selling', '--journal', 'MS')
        self.assertEqual(result['graph']['anchors'], [])
        self.assertEqual(result['coverage']['pdf_files'], 3)
        self.assertEqual([p['id'] for p in result['retrieval']['papers']], [2])
        self.assertEqual(result['retrieval']['papers'][0]['pages'][0]['pdf_page'], 4)
        self.assertEqual(result['retrieval']['queries'][0]['match'], 'phrase')

    def test_two_search_channels_and_query_fusion(self):
        result = self.run_tool('brief', '代理模式', '--phrase', 'agency selling', '--term', 'revenue sharing')
        hit = {p['id']: p for p in result['retrieval']['papers']}
        self.assertEqual(set(hit), {1, 2})
        self.assertIn('agency selling', hit[1]['title_queries'])
        self.assertEqual(hit[1]['pages'][0]['text_source'], 'ocr')
        self.assertIn('revenue sharing', hit[2]['title_queries'])

    def test_evidence_preserves_actual_page_and_ocr_source(self):
        result = self.run_tool('evidence', '1', '--page', '4', '--chars', '12')
        self.assertEqual(result['pages'][0]['pdf_page'], 4)
        self.assertEqual(result['pages'][0]['text_source'], 'ocr')
        self.assertTrue(result['pages'][0]['truncated'])
        with self.assertRaisesRegex(ValueError, 'physical pages'):
            self.run_tool('evidence', '1', '--page', '9')
        with self.assertRaisesRegex(ValueError, 'No verified proof'):
            self.run_tool('evidence', '1', '--section', 'proof')

    def test_validation_rejects_verified_edge_without_evidence(self):
        broken = json.loads(DEFAULT_GRAPH.read_text(encoding='utf-8'))
        reviewed = next(edge for edge in broken['edges'] if edge['review'] == 'verified')
        reviewed['evidence'] = []
        fixture = Path(self.directory.name) / 'invalid.json'
        fixture.write_text(json.dumps(broken), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Evidence required'):
            Graph(fixture)

    def test_topic_with_no_query_reports_search_not_run(self):
        result = self.run_tool('brief', '未命中任何主题')
        self.assertFalse(result['retrieval']['queries'])
        self.assertTrue(any('No lexical search was run' in note for note in result['notes']))

    def test_named_paper_seeds_phrase_query_without_topic(self):
        result = self.run_tool('brief', '--anchor', 'moorthy-2023', '--intent', 'compare')
        self.assertEqual(result['graph']['anchors'], ['moorthy-2023'])
        self.assertEqual(result['retrieval']['queries'][0]['match'], 'phrase')
        self.assertIn('Hotelling', result['retrieval']['queries'][0]['query'])


if __name__ == '__main__':
    unittest.main()
