"""Current requirement descriptions never certify a measured cell."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'MCP'))
from crystal_108d import live_cell


def source():
    return json.loads((ROOT/'MCP/data/live_cell_constitution.json').read_text(encoding='utf-8'))


def cache(data):
    return patch.object(live_cell, '_CELL', Mock(load=Mock(return_value=data)))


class LiveCellRequirementTests(unittest.TestCase):
    def test_all_seven_ids_names_and_descriptions_read_exact_source(self):
        data = source()
        for query in [live_cell.query_live_cell, lambda _: live_cell.live_cell_status()]:
            report = query('all')
            self.assertIn(data['description'], report)
            self.assertIn(data['alive_threshold'], report)
            for record in data['requirements']:
                self.assertIn(f"{record['id']}: {record['name']}", report)
                self.assertIn(record['description'], report)
            self.assertIn('HOLD', report)
            self.assertNotIn('PASS', report)
            self.assertNotIn('**Schemas**', report)

    def test_exact_requirement_id_and_name_no_partial_match_or_wrong_route(self):
        data = source()
        for record in data['requirements']:
            for selector in [record['id'], record['name'].lower()]:
                report = live_cell.query_live_cell('requirement:'+selector)
                self.assertIn(f"### {record['id']}: {record['name']}", report)
                self.assertIn(record['description'], report)
                self.assertEqual(report.count('### LC'), 1)
        for selector in ['', 'LC', 'Address', 'LC0', 'LC8']:
            self.assertIn('Unknown', live_cell.query_live_cell('requirement:'+selector))

    def test_absent_legacy_schema_routes_hold_without_default_assertions(self):
        for selector in ['schemas','schema:BoardStateRow','schema:TraceCert','metro','station:M60','liminal','soul','route']:
            report = live_cell.query_live_cell(selector)
            self.assertTrue(report.startswith('HOLD:'), report)
            self.assertNotIn('PASS', report)
            self.assertNotIn('**Full Signature**', report)
        self.assertIn('Unknown', live_cell.query_live_cell('undeclared'))

    def test_caller_booleans_never_become_a_liveness_certificate(self):
        # This reader has no certificate API: direct objects reject, JSON text remains an unknown selector.
        assertions = {f'LC{i}': True for i in range(1,8)}
        for value in [True, assertions, json.dumps(assertions), '{}']:
            report = live_cell.query_live_cell(value)
            self.assertTrue('Invalid' in report or 'Unknown' in report)
            self.assertNotIn('PASS', report)
            self.assertNotIn('ALIVE', report)
            self.assertNotIn('verified', report.lower())
        for value in [None, [], 1, '', '   ']:
            self.assertIn('Invalid', live_cell.query_live_cell(value))

    def test_missing_conflicting_source_records_never_get_fallback_readiness(self):
        original = source()
        mutations = [lambda d: d.pop('requirements'),lambda d: d.update(requirements=[]),
                     lambda d: d['requirements'].pop(),lambda d: d['requirements'].append(d['requirements'][0]),
                     lambda d: d['requirements'][0].pop('description'),lambda d: d.pop('alive_threshold'),
                     lambda d: d.update(requirements={}),
                     lambda d: d['meta'].update(version='unknown'),lambda d: d.update(cell_schema={}),
                     lambda d: (d.pop('requirements'), d.update(cell_schema={'BoardStateRow':dict(version=1,description='archive row',fields={'thread_id':'ID'})}))]
        for mutate in mutations:
            data = copy.deepcopy(original); mutate(data)
            with cache(data):
                self.assertTrue(live_cell.query_live_cell('all').startswith('HOLD:'))
                self.assertTrue(live_cell.live_cell_status().startswith('HOLD:'))

    def test_unreadable_malformed_source_holds(self):
        for data in [None, [], {}, {'meta':None}, {'meta':[]}]:
            with cache(data):
                self.assertTrue(live_cell.query_live_cell('all').startswith('HOLD:'))
                self.assertTrue(live_cell.live_cell_status().startswith('HOLD:'))
        for error in [FileNotFoundError('missing'), PermissionError('read'), ValueError('JSON')]:
            with patch.object(live_cell, '_CELL', Mock(load=Mock(side_effect=error))):
                self.assertTrue(live_cell.live_cell_status().startswith('HOLD:'))

    def test_query_does_not_mutate_shared_source(self):
        data=source(); before=copy.deepcopy(data)
        with cache(data):
            live_cell.query_live_cell('all'); live_cell.query_live_cell('requirement:LC1'); live_cell.live_cell_status()
        self.assertEqual(data,before)

    def test_supported_legacy_schema_read_remains(self):
        from crystal_108d.registry_sources import load_archive
        data, _ = load_archive('live_cell_constitution.json')
        schema = data['cell_schema']['BoardStateRow']
        with cache(data):
            self.assertIn(f"`thread_id`: {schema['fields']['thread_id']}",live_cell.query_live_cell('schema:BoardStateRow'))
            self.assertIn(schema['description'],live_cell.query_live_cell('schemas'))
            self.assertIn('Catalog Snapshot SHA256',live_cell.query_live_cell('schema:BoardStateRow'))
            self.assertIn('not found',live_cell.query_live_cell('schema:BoardState'))
            self.assertIn('not found',live_cell.query_live_cell('schema:'))



if __name__ == '__main__':
    unittest.main()
