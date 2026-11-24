"""Guard the evidence boundaries of scoped and no-indexed-citation discovery."""

from contextlib import closing, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

import citation_claims as claims
import corpus_rag as rag
import corpus_semantics as sem
import model_comparison as comparison
import paperlist


class SemanticDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.refs = [dict(id=key, author=author, year=year, page=18)
                     for key, author, year in ((1, 'Smith', 2001), (2, 'Jones', 2004))]
        self.matcher, self.owners = sem.citation_matcher(self.refs)
        self.doc = {'id': 3, 'year': 2017}

    def expanded(self, text, previous=None, page=4, section='model'):
        return list(sem.expanded_relations(
            (302, text, page, section, 'Model'), previous, self.matcher, self.owners, self.doc))

    def test_cross_sentence_and_two_locators(self):
        anchor = 'Smith (2001) develops a model in which all firms take exogenous advertising rates.'
        own = 'By contrast, our model allows advertising rates to be endogenous.'
        row = self.expanded(anchor + ' ' + own)
        self.assertEqual([(r[0], r[4], r[10]) for r in row], [(1,'endogenizes','adjacent_sentences')])
        tail = anchor[-65:]
        row = self.expanded(tail + ' ' + own,
                            (301, anchor, 4, 'model', 'Model'))
        self.assertEqual(len(row),1)
        snippets = json.loads(row[0][11])
        self.assertEqual([p['passage'] for p in snippets], [301,302])
        self.assertEqual([p['excerpt'] for p in snippets], [anchor,own])
        self.assertEqual(self.expanded(tail + ' ' + own, (301, anchor, 3, 'model', 'Model')), [])

    def test_group_requires_explicit_scope(self):
        text = ('Several economic models are informative: Smith (2001) and Jones (2004). '
                'These papers assume exogenous advertising rates and no intermediaries. '
                'By contrast, our model allows advertising rates to be endogenous.')
        self.assertEqual([(r[0],r[4]) for r in self.expanded(text)], [(1,'endogenizes'),(2,'endogenizes')])
        self.assertFalse(self.expanded(text.replace('These papers assume', 'Recent studies assume')))
        self.assertFalse(self.expanded(text.replace('By contrast,', 'Another paper enters this debate. By contrast,')))
        self.assertFalse(self.expanded(text.replace('advertising rates to be endogenous',
                                                   'retail prices to be endogenous')))

    def test_ordinal_never_assigns_other_paper(self):
        text = ('We review two papers: Smith (2001) and Jones (2004). '
                'The first examines sequential price decisions after retailers receive private information. '
                'Their equilibrium is interpretable as a restricted case of our framework.')
        self.assertEqual([(r[0],r[4]) for r in self.expanded(text)], [(1,'maps_model_component')])
        self.assertEqual([(r[0],r[4]) for r in self.expanded(text.replace('The first','The second'))],
                         [(2,'maps_model_component')])

    def test_attribution_is_not_a_semantic_relation(self):
        text = 'Smith (2001) shows that reducing wholesale prices lowers welfare in equilibrium.'
        self.assertEqual(list(claims.extract(text,self.matcher,self.owners,3,302,4,'model')),
                         [(3,1,'attributed_theory_result',4,302,'model',18,text)])
        self.assertFalse(self.expanded(text))
        unrelated = 'Many papers examine supply chains, including Smith (2001) and Jones (2004).'
        self.assertFalse(list(claims.extract(unrelated,self.matcher,self.owners,3,302,4,'model')))
        ambiguous = 'Smith (2001) and Peters (2009) show that prices fall in equilibrium.'
        self.assertFalse(list(claims.extract(ambiguous,self.matcher,self.owners,3,302,4,'model')))

    def test_no_pair_from_negation_or_different_primitives(self):
        for text in [
            'We do not assume exogenous advertising rates in this setting.',
            'We model seller behavior where advertising rates are stable and search costs are exogenous.',
            'The online appendix extends our model to allow advertising rates to be endogenous.',
            'Our analysis suggests that advertising rates might be endogenous in the other setting.',
        ]:
            self.assertFalse(list(comparison.evidence(text,'model',{'advertising_rates'})))

    def test_paired_evidence_and_attribution_index(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source, rdb, adb = (root/x for x in ('source.db','rag.db','claims.db'))
            with closing(paperlist.connect(source,writable=True)):
                pass
            with closing(rag.connect(rdb, True)) as corpus, corpus:
                corpus.execute('INSERT INTO config VALUES (?,?)',('source',str(source)))
                rows = [
                    (1,'Smith',2001,'We assume that advertising rates are exogenous in our pricing model.'),
                    (2,'Jones',2004,'We assume that advertising rates are endogenous in our pricing model.'),
                    (3,'Chen',2010,'Smith (2001) shows that advertising rates affect equilibrium welfare.'),
                ]
                for key, author, year, text in rows:
                    corpus.execute('INSERT INTO docs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                                   (key,f'MS/{author}.pdf',f'Title {author}',author,year,'MS',
                                    'stamp',None,1,1,'heading',0))
                    corpus.execute('INSERT INTO passages(rowid,text,paper,page,section,heading) VALUES (?,?,?,?,?,?)',
                                   (key*rag.PASSAGE_BASE,text,key,2,'model','Model'))
                corpus.execute('INSERT INTO links VALUES (?,?,?,?,?)',(3,1,7,'section_title_author_year','Smith'))
            with redirect_stdout(io.StringIO()):
                claims.build(rdb,adb,limit=1)
                claims.build(rdb,adb)
                claims.build(rdb,adb)
            with closing(claims.connect(adb)) as con, closing(rag.connect(rdb)) as corpus:
                self.assertEqual(claims.status(con,corpus)['distinct_citation_pairs'],1)
                a = claims.search(con,corpus,[1],['advertising welfare'],'future')
                self.assertEqual(a['claims'][0]['excerpt'],rows[2][-1])
                p = comparison.compare(corpus,[1],['advertising rates'])
                self.assertEqual(len(p['pairs']),1)
                pair = p['pairs'][0]
                self.assertEqual([e['paper_id'] for e in pair['evidence']], [1,2])
                self.assertEqual([e['value'] for e in pair['evidence']], ['exogenous','endogenous'])
                self.assertEqual(pair['state'],'comparison_hypothesis')
            with closing(rag.connect(rdb, True)) as corpus, corpus:
                corpus.execute('INSERT INTO links VALUES (?,?,?,?,?)',(2,1,7,'section_title_author_year','Smith'))
                self.assertFalse(comparison.compare(corpus,[1],['advertising rates'])['pairs'])


if __name__ == '__main__':
    unittest.main()
