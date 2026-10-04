"""Source descriptions do not constitute conservation or emergence certificates."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'MCP'))
from crystal_108d import conservation, stage_codes, emergence


def source(name):
    return json.loads((ROOT / 'MCP/data' / name).read_text(encoding='utf-8'))


def cache(module, name, data):
    return patch.object(module, name, Mock(load=Mock(return_value=data)))


class DescriptiveRegistryTests(unittest.TestCase):
    def test_all_six_conservation_laws_are_literal_source_descriptions(self):
        data = source('conservation_laws.json')
        report = conservation.query_conservation('list')
        self.assertEqual(len(data['laws']), 6)
        for law in data['laws']:
            for key in ('id', 'name', 'statement', 'invariant'):
                self.assertIn(law[key], report)
        self.assertIn(data['verification_frequency'], report)
        self.assertIn('HOLD', report)
        self.assertNotIn('Cert Class', report)

    def test_v2_empty_partial_and_delta_balanced_objects_never_certify(self):
        for text in ['{}', '{"shell_deltas":[]}', '{"shell_deltas":[0]}',
                     json.dumps(dict(shell_deltas=[1,-1], zoom_deltas=[0], wreath_rotations=[0],
                                     archetype_shifts=[0], face_shifts=[0], mobius_flips=0))]:
            report = conservation.query_conservation(text)
            self.assertNotIn('PASS', report)
            self.assertNotIn('Cert Class', report)
            self.assertTrue('Invalid' in report or 'HOLD' in report)

    def test_conservation_invalid_json_shapes_and_text_inputs(self):
        for value in [None, [], True, '', ' ', '[1]', 'null', 'true', '42', '"x"', '{']:
            report = conservation.query_conservation(value)
            self.assertIn('Invalid', report)
            self.assertNotIn('PASS', report)

    def test_v2_metadata_loss_cannot_enable_archived_certification(self):
        data = source('conservation_laws.json')
        motion = json.dumps(dict(shell_deltas=[0], zoom_deltas=[0], wreath_rotations=[0],
                                 archetype_shifts=[0], face_shifts=[0], mobius_flips=0))
        for mutate in [lambda d: d.pop('meta'), lambda d: d.update(meta=None),
                       lambda d: d['meta'].update(version='unknown')]:
            altered = copy.deepcopy(data); mutate(altered)
            with cache(conservation, '_laws', altered):
                self.assertNotIn('PASS', conservation.query_conservation(motion))
        with cache(conservation, '_laws', {'meta': {'version': 'unknown'}}):
            self.assertTrue(conservation.query_conservation(motion).startswith('HOLD:'))

    def test_unknown_legacy_version_cannot_certify_complete_motion(self):
        data = dict(meta=dict(version='unknown', master_invariant='legacy'),
                    laws=[dict(index=i, check_rule='archived predicate') for i in range(1, 7)])
        motion = json.dumps(dict(shell_deltas=[0], zoom_deltas=[0], wreath_rotations=[0],
                                 archetype_shifts=[0], face_shifts=[0], mobius_flips=0))
        for version in ['unknown', '3.0', None]:
            data['meta']['version'] = version
            with cache(conservation, '_laws', data):
                report = conservation.query_conservation(motion)
                self.assertTrue(report.startswith('HOLD:'))
                self.assertNotIn('PASS', report)
                self.assertNotIn('Cert Class', report)

    def test_missing_unreadable_and_malformed_source_families_hold(self):
        consumers = [(conservation, '_laws', lambda: conservation.query_conservation('list')),
                     (stage_codes, '_stages', lambda: stage_codes.query_stage_code('all')),
                     (emergence, '_EMERGENCE', lambda: emergence.query_emergence('all')),
                     (emergence, '_EMERGENCE', emergence.emergence_status)]
        for module, name, query in consumers:
            for data in [None, [], 1, {}, {'meta': None}, {'meta': []}]:
                with cache(module, name, data):
                    self.assertTrue(query().startswith('HOLD:'))
            for error in [FileNotFoundError('missing source'), PermissionError('no read'), ValueError('invalid JSON')]:
                with patch.object(module, name, Mock(load=Mock(side_effect=error))):
                    self.assertTrue(query().startswith('HOLD:'))

    def test_source_law_missing_duplicate_incomplete_records_hold(self):
        original = source('conservation_laws.json')
        for mutate in [lambda d: d.pop('laws'), lambda d: d.update(laws=None),
                       lambda d: d['laws'].pop(), lambda d: d['laws'].append(d['laws'][0]),
                       lambda d: d['laws'][0].pop('invariant'), lambda d: d.pop('verification_frequency')]:
            data = copy.deepcopy(original); mutate(data)
            with cache(conservation, '_laws', data):
                self.assertTrue(conservation.query_conservation('list').startswith('HOLD:'))
                self.assertNotIn('PASS', conservation.query_conservation('{"observed":true}'))

    def test_legacy_motion_requires_each_measurement_and_rejects_invalid_values(self):
        valid = dict(shell_deltas=[1,-1], zoom_deltas=[0], wreath_rotations=[0],
                     archetype_shifts=[0], face_shifts=[0], mobius_flips=0)
        legacy = dict(meta=dict(version='1.0', master_invariant='legacy motion predicates'),
                      laws=[dict(index=i, check_rule='archived predicate') for i in range(1, 7)])
        with cache(conservation, '_laws', legacy):
            self.assertIn('ALL PASS', conservation.query_conservation(json.dumps(valid)))
            bad = dict(valid, shell_deltas=[1]); self.assertIn('FAIL', conservation.query_conservation(json.dumps(bad)))
            for key in valid:
                bad = copy.deepcopy(valid); del bad[key]
                self.assertIn('Invalid', conservation.query_conservation(json.dumps(bad)))
            for field, values in [('shell_deltas', []), ('shell_deltas', [True]),
                                  ('zoom_deltas', [float('nan')]), ('shell_deltas', [1e308,1e308]),
                                  ('zoom_deltas', [1.0]), ('face_shifts', ['1']),
                                  ('mobius_flips', False), ('mobius_flips', -1), ('mobius_flips', 1.5)]:
                bad = dict(valid); bad[field] = values
                self.assertIn('Invalid', conservation.query_conservation(json.dumps(bad)))
            self.assertNotIn('PASS', conservation.query_conservation('{}'))

    def test_all_five_stage_records_and_totals_preserve_final_ambiguity(self):
        data = source('stage_codes.json')
        self.assertEqual(len(data['stages']), 5)
        overview = stage_codes.query_stage_code('all')
        for code, stage in data['stages'].items():
            for report in [overview, stage_codes.query_stage_code(' '+code.lower()+' ')]:
                for value in [f'Stage {code}', str(stage['waves']), stage['description'], stage['focus']]:
                    self.assertIn(value, report)
        for value in ['159', '477', 'including FINAL = 160', 'HOLD']:
            self.assertIn(value, overview)
        self.assertNotIn('Dimension', overview)

    def test_unmapped_stage_selectors_never_get_fabricated_dimension(self):
        for selector in ['S3', 'S4', 'S12', 'A+', 'Omega', 'zeros', 'hubs', 'sigma60']:
            report = stage_codes.query_stage_code(selector)
            self.assertTrue(report.startswith('HOLD:'), report)
            self.assertNotIn('**Dimension**', report)
        for selector in [None, 1, [], '', '   ']:
            self.assertIn('Invalid', stage_codes.query_stage_code(selector))

    def test_missing_invalid_stage_records_and_counters_hold(self):
        original = source('stage_codes.json')
        for mutate in [lambda d: d.pop('stages'), lambda d: d.update(stages=[]),
                       lambda d: d['stages'].pop('FINAL'), lambda d: d['stages']['A'].update(waves=True),
                       lambda d: d['stages']['B'].pop('focus'), lambda d: d.pop('total_per_cycle')]:
            data = copy.deepcopy(original); mutate(data)
            with cache(stage_codes, '_stages', data):
                self.assertTrue(stage_codes.query_stage_code('all').startswith('HOLD:'))

    def test_all_six_emergence_records_exact_pair_and_source_positions(self):
        data = source('dimensional_emergence.json')
        self.assertEqual(len(data['emergence_sequence']), 6)
        all_report = emergence.query_emergence('all')
        status = emergence.emergence_status()
        for pos, record in enumerate(data['emergence_sequence'], 1):
            for report in [all_report, status, emergence.query_emergence(f'phase:{pos}'),
                           emergence.query_emergence(f"phase:{record['from']} -> {record['to']}")]:
                for value in [f'Source sequence position {pos}', record['mechanism'], str(record['gates']),
                              f"{record['from']} -> {record['to']}"]:
                    self.assertIn(value, report)
                self.assertIn('HOLD', report)
                self.assertNotIn('**Transport Gained**', report)

    def test_emergence_bounds_ambiguous_pair_and_unsupported_proofs(self):
        for selector in ['phase:0', 'phase:7', 'phase:'+'9'*5000]:
            self.assertIn('Invalid', emergence.query_emergence(selector))
        self.assertIn('Source sequence position 1', emergence.query_emergence('phase:'+'0'*5000+'1'))
        for selector in ['phase:4D', 'phase:4D->6D', 'kernel', 'lenses', 'lens:6D', 'bodies']:
            self.assertTrue(emergence.query_emergence(selector).startswith('HOLD:'))
        for selector in [None, 1, [], '', '  ']:
            self.assertIn('Invalid', emergence.query_emergence(selector))
        self.assertIn('Unknown', emergence.query_emergence('undeclared'))

    def test_emergence_conflicting_missing_records_hold(self):
        original = source('dimensional_emergence.json')
        for mutate in [lambda d: d.pop('emergence_sequence'), lambda d: d.update(emergence_sequence=[]),
                       lambda d: d['emergence_sequence'].pop(2),
                       lambda d: d['emergence_sequence'].append(d['emergence_sequence'][0]),
                       lambda d: d['emergence_sequence'][0].update(gates=[True]),
                       lambda d: d['emergence_sequence'][0].pop('mechanism')]:
            data = copy.deepcopy(original); mutate(data)
            with cache(emergence, '_EMERGENCE', data):
                self.assertTrue(emergence.query_emergence('all').startswith('HOLD:'))
                self.assertTrue(emergence.emergence_status().startswith('HOLD:'))

    def test_source_invariant_text_is_never_executed(self):
        data = source('conservation_laws.json')
        data['laws'][0]['invariant'] = "__import__('os').system('must-not-run')"
        with cache(conservation, '_laws', data), patch('os.system', side_effect=AssertionError('executed')):
            self.assertIn(data['laws'][0]['invariant'], conservation.query_conservation('list'))
            self.assertNotIn('PASS', conservation.query_conservation('{"measurement":1}'))

    def test_valid_legacy_stage_and_emergence_branches_remain(self):
        stage = dict(code='S3', dimension=3, body_type='seed', description='legacy seed', object='body', carrier='carrier')
        data = dict(meta=dict(ladder='S3', liminal_coordinate='x'), stages=[stage])
        with cache(stage_codes, '_stages', data):
            self.assertIn('legacy seed', stage_codes.query_stage_code('all'))
            self.assertIn('**Dimension**: 3D', stage_codes.query_stage_code('S3'))
        phase = dict(index=1, name='legacy', **{'from':'3D','to':'4D'}, mechanism='mechanism',
                     lens_state='square', body_gained='body', transport_gained=['layer'], key_object='object', description='desc')
        data = dict(emergence_phases=[phase], meta=dict(path='3D->4D', governing_law='law',
                     kernel_embedding_law='kernel', total_phases=1, source='legacy'))
        with cache(emergence, '_EMERGENCE', data):
            self.assertIn('**Transport Gained**: layer', emergence.query_emergence('phase:1'))
            self.assertIn('**Governing Law**: law', emergence.emergence_status())


if __name__ == '__main__':
    unittest.main()
