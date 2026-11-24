"""Regression tests for candidate extraction and graph traversal."""

from contextlib import closing, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

import corpus_rag as rag
import corpus_semantics as sem
import research_agent as agent


class SemanticsTest(unittest.TestCase):
    def extract(self, text, refs=None, year=2020, page=2, section='model'):
        if refs is None:
            refs = [dict(id=1, author='Smith', year=2010, page=9)]
        matcher, owners = sem.citation_matcher(refs)
        return sem.extract_relations(text, matcher, owners, dict(id=2, year=year), 40, page, section)

    def test_explicit_relations(self):
        for text, kind in [
            ('We extend the model of Smith (2010) by introducing an outside option.', 'extends_component'),
            ('Unlike Smith (2010), our model allows asymmetric firms.', 'contrasts_assumptions'),
            ('Our results contrast sharply with the results in Smith (2010).', 'contrasts_results'),
            ('Our results are consistent with Smith (2010) for highly patient firms.', 'supports_result'),
            ('We show that the results of Smith (2010) hold only in competitive retail markets.', 'limits_result'),
        ]:
            with self.subTest(kind=kind):
                result, context, _ = self.extract(text)
                self.assertEqual(context, {1})
                self.assertEqual(result, [(1, 2, 2010, 2020, kind, 40, 2, 'model', 9, text)])

    def test_no_edge_for_citation_or_ambiguous_targets(self):
        for text in ('Smith (2010) studies retail competition.',
                     'We extend Smith (2010) and Jones (2015) by adding a seller.'):
            self.assertFalse(self.extract(text)[0])
        text = 'Unlike Smith (2010), our model allows asymmetric firms.'
        collision = [dict(id=i, author='Smith', year=2010, page=9) for i in (1, 3)]
        self.assertFalse(self.extract(text, refs=collision)[0])
        self.assertFalse(self.extract(text, year=2009)[0])
        self.assertFalse(self.extract(text, page=9)[0])
        self.assertFalse(self.extract(text, section='endmatter')[0])

    def test_resumable_index_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rpath, spath, source = (root / n for n in ('rag.db', 'sem.db', 'source.db'))
            with closing(agent.paperlist.connect(source, writable=True)) as original, original:
                original.execute('INSERT INTO settings VALUES (?,?)', ('root', str(root)))
            with closing(rag.connect(rpath, True)) as corpus, corpus:
                corpus.execute('INSERT INTO config VALUES (?,?)', ('source', str(source)))
                for key, author, year, body in [
                    (1, 'Smith', 2000, 'Wholesale pricing lets retailers compete.'),
                    (2, 'Jones', 2010, 'We extend Smith (2000) by adding wholesale pricing. '
                     'We assume that retailers can enter the market in stage one.'),
                    (3, 'Cheng', 2020, 'Unlike Jones (2010), we assume that all retailers are active. '
                     'Proposition 1. In equilibrium retailers always choose separate markets when costs are low.'),
                ]:
                    corpus.execute('INSERT INTO docs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                                   (key, f'MS/{author}.pdf', f'Paper {key}', author, year, 'MS',
                                    'stamp', None, 1, 1, 'heading', 0))
                    corpus.execute('INSERT INTO passages(rowid,text,paper,page,section,heading) VALUES (?,?,?,?,?,?)',
                                   (key*rag.PASSAGE_BASE, body, key, 2, 'model', 'Model'))
                corpus.executemany('INSERT INTO links VALUES (?,?,?,?,?)',
                                   [(2, 1, 9, 'section_title_author_year', 'Smith'),
                                    (3, 2, 9, 'section_title_author_year', 'Jones')])
            def build(*extra):
                with redirect_stdout(io.StringIO()):
                    sem.build(sem.parser().parse_args(['--db', str(spath), '--corpus-db', str(rpath), 'build', *extra]))
            build('--limit', '1')
            with closing(sem.connect(spath)) as con, closing(rag.connect(rpath)) as corpus:
                self.assertEqual(sem.status(con, corpus)['scanned_pdfs'], 1)
            build()
            build()
            with closing(sem.connect(spath)) as con, closing(rag.connect(rpath)) as corpus:
                status = sem.status(con, corpus)
                self.assertEqual(status['scans_missing_or_stale_by_document_stamp'], 0)
                self.assertEqual(status['distinct_relation_pairs'], 2)
                self.assertEqual(status['statement_candidates']['proposition'], 1)
                config = sem.check_bindings(con, corpus, rpath, source)
                result = sem.contextualize(con, corpus, config, ['wholesale pricing'], [3], 'past', 2, 8)
                self.assertIn('channels', [c['id'] for c in result['concepts']])
                self.assertEqual([r['paper']['id'] for r in result['timeline']], [1, 2, 3])
                self.assertEqual(sem.paths(con, corpus, 1, 3, 2)['paths'][0]['papers'], [1, 2, 3])
            args = agent.parser().parse_args(['--db', str(source), '--corpus-db', str(rpath),
                                             '--semantic-db', str(spath), 'brief', '--intent', 'lineage',
                                             '--citation-seed', '3'])
            result = agent.run(args, agent.Graph(agent.DEFAULT_GRAPH))
            self.assertEqual(result['graph']['relations'], [])
            self.assertTrue(result['corpus_rag']['semantic_graph']['relation_candidates'])
            with closing(rag.connect(rpath, True)) as corpus, corpus:
                corpus.execute('DELETE FROM links WHERE citing=3')
            with closing(sem.connect(spath)) as con, closing(rag.connect(rpath)) as corpus:
                self.assertEqual(sem.paths(con, corpus, 1, 3, 2)['paths'], [])
            build()
            with closing(sem.connect(spath)) as con, closing(rag.connect(rpath)) as corpus:
                self.assertEqual(sem.status(con, corpus)['distinct_relation_pairs'], 1)


if __name__ == '__main__':
    unittest.main()
