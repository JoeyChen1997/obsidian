"""Ensure that discovery does not turn source candidates into reviewed works."""

import sqlite3
import unittest

from reading_coverage import coverage


class FixtureGraph:
    papers = {
        'registered': {'pdf': 'MS/a.pdf', 'reading_status': 'core_read',
                       'title': 'Comparative Statics of Distribution Channels', 'year': 2013},
        'missing': {'reading_status': 'source_gap', 'title': 'Another Paper'},
    }

    def node(self, key):
        return self.papers[key]


class CoverageTest(unittest.TestCase):
    def test_candidates_do_not_inherit_reading_status(self):
        con = sqlite3.connect(':memory:')
        self.addCleanup(con.close)
        con.row_factory = sqlite3.Row
        con.execute('CREATE TABLE papers(id,relpath,journal,year,title_hint,author_hint,status,pages,text_pages)')
        title = 'Comparative Statics of Distribution Channels'
        con.executemany('INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?)', [
            (1, 'MS/a.pdf', 'MS', 2012, title, 'A', 'indexed', 10, 10),
            (2, 'MS/b.pdf', 'MS', 2013, title, 'A', 'partial', 10, 8),
            (3, 'MS/c.pdf', 'MS', 2013, title, 'A', 'missing', 10, 8),
        ])
        stats, rows, families = coverage(con, FixtureGraph())
        self.assertEqual(stats['present_pdf_records'], 2)
        self.assertEqual(stats['present_unresolved_pdf_identities'], 1)
        self.assertEqual(stats['present_by_reading_state'], {'core_read': 1, 'not_reviewed': 1})
        self.assertEqual(stats['present_source_issues'], {'partial_indexed_text': 1})
        self.assertEqual(stats['graph_nodes_without_catalog_source'][0]['id'], 'missing')
        self.assertEqual(list(families.values()), [[1, 2]])
        self.assertEqual(rows[0]['publication_year'], 2013)
        self.assertIsNone(rows[1]['work_id'])
        self.assertEqual(rows[2]['source_issue'], 'missing')
