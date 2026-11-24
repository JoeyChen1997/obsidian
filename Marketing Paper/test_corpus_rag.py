"""Regression tests for the automatically built Paperlist evidence layer."""

from contextlib import closing, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

import corpus_rag as rag
import paperlist
from research_agent import DEFAULT_GRAPH, Graph, parser, run


class CorpusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / 'source.sqlite3'
        self.rag = root / 'passages.sqlite3'
        with closing(paperlist.connect(self.source, writable=True)) as con, con:
            con.execute("INSERT INTO settings VALUES ('root',?)", (str(root),))
            for key, who, year, title, pages in (
                (1,'Müller',2004,'Product Variety in Platform Markets',[
                    'Abstract. Earlier sellers choose agency contracts.\n1. Introduction\nThese are platform markets.',
                    '2. The Model\nAgency selling contracts set a wholesale price.']),
                (2,'Smith',2014,'Retail Prices Under Agency Selling',[
                    'Abstract. Agency selling determines market organization.\n1. Introduction\nMüller (2004) changes the timing.',
                    '2. Model\nConsider agency selling with a monopoly platform.\nReferences\nMüller D (2004). Product Variety in',
                    'Platform Markets. Marketing Science 20 31.\nAppendix\nThe proof uses competing offers.']),
                (3,'Yang',2021,'Information Sharing and Pass Through',[
                    '1. Main Results\nRetail rates pass through.\nReferences\nSmith J (2014) Retail Prices Under Agency Selling.\n'
                    'Jones (2008) Product Variety in Platform Markets.']),
                (4,'Li',2024,'Market Design in Online Retail',[
                    'Download copy.\nYang L (2021) Information Sharing and Pass Through.']),
            ):
                rel = f'MKSC/{who}_{year}_{title}.pdf'
                con.execute('''INSERT INTO papers VALUES (?,?,?,?,?,?,1,1,'indexed',?,?,NULL)''',
                            (key,rel,'MKSC',who,year,title,len(pages),len(pages)))
                con.execute('INSERT INTO catalog(rowid,title,author) VALUES(?,?,?)',(key,title,who))
                con.executemany('INSERT INTO page_index(rowid,paper_id,pdf_page,body) VALUES(?,?,?,?)',
                                ((key*paperlist.PAGE_STRIDE+i,key,i,body) for i,body in enumerate(pages,1)))
        self.args = rag.parser().parse_args(['--db',str(self.rag),'build','--source',str(self.source)])
        with redirect_stdout(io.StringIO()):
            rag.build(self.args)

    def test_exact_reference_crosses_physical_pages_and_does_not_guess_ambiguous_citations(self):
        with closing(rag.connect(self.rag)) as con:
            edges = [tuple(r) for r in con.execute('SELECT citing,cited,page,method FROM links ORDER BY citing,cited')]
        self.assertEqual(edges,[(2,1,2,'section_title_author_year'),(3,2,1,'section_title_author_year'),
                                (4,3,1,'tail_title_author_year')])

    def test_section_and_page_provenance(self):
        with closing(rag.connect(self.rag)) as con:
            results = rag.passage_search(con,[],['agency selling'],section='model',limit=8)
        self.assertEqual({x['paper'] for x in results['papers']},{1,2})
        self.assertTrue(all(p['hits'][0]['page']==2 for p in results['papers']))

    def test_multihop_and_tentative_policy(self):
        with closing(rag.connect(self.rag)) as con:
            strict = rag.neighborhood(con,[1],'future',3,18,False)
            with_tail = rag.neighborhood(con,[1],'future',3,18,True)
        self.assertEqual([e['citing'] for e in strict['edges']],[2,3])
        self.assertEqual([e['hop'] for e in with_tail['edges']],[1,2,3])

    def test_body_context_from_source(self):
        with closing(rag.connect(self.rag)) as con, closing(paperlist.connect(self.source)) as src:
            result = rag.citation_context(con,src,2,1)
        self.assertEqual(result['body_candidates'][0]['page'],1)
        self.assertIn('changes the timing',result['body_candidates'][0]['excerpt'])

    def test_incremental_removed_paper_has_no_stale_edges(self):
        with closing(paperlist.connect(self.source,writable=True)) as src, src:
            src.execute("UPDATE papers SET status='missing' WHERE id=1")
        with redirect_stdout(io.StringIO()):
            rag.build(self.args)
        with closing(rag.connect(self.rag)) as con:
            self.assertEqual(rag.stats(con)['papers'],3)
            self.assertFalse(rag.neighborhood(con,[1],'future',2,8,True)['edges'])

    def test_agent_fusion_and_citations_on_unmapped_topic(self):
        args = parser().parse_args(['--db',str(self.source),'--corpus-db',str(self.rag),'brief',
                                    '代理销售渠道','--intent','lineage','--phrase','agency selling'])
        result = run(args,Graph(DEFAULT_GRAPH))
        self.assertFalse(result['graph']['anchors'])
        rich = result['corpus_rag']
        self.assertEqual(rich['coverage']['documents'],4)
        self.assertTrue(any('section_passages' in p['channels'] for p in rich['ranked_candidates']))
        self.assertTrue(rich['citation_candidates']['future']['edges'])


if __name__ == '__main__':
    unittest.main()
