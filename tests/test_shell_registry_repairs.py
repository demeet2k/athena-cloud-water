"""Bounded source-bound shell/catalog queries; no corpus or server writes."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'MCP'))
from crystal_108d import shells


def source(name):
    return json.loads((ROOT / 'MCP/data' / name).read_text(encoding='utf-8'))


class ShellRegistryTests(unittest.TestCase):
    def test_all_36_source_shells_and_four_faces(self):
        data = source('shell_registry.json')
        self.assertEqual(len(data['shells']), 36)
        for key, record in data['shells'].items():
            report = shells.query_shell(int(key))
            for value in (record['archetype'], record['phase'], record['element_primary'],
                          f"S{record['mirror_shell']}", str(record['neighbors'])):
                self.assertIn(value, report)
            for face in record['faces'].values():
                self.assertIn(face['address'], report)
                self.assertIn(face['gate'], report)
            self.assertIn('HOLD', report)
            self.assertNotIn('**Nodes**', report)

    def test_all_12_archetypes_and_declared_members(self):
        data = source('shell_registry.json')
        self.assertEqual(len(data['archetypes']), 12)
        for key, record in data['archetypes'].items():
            report = shells.query_archetype(key)
            for value in (record['name'], record['phase'], record['element']):
                self.assertIn(value, report)
            for n in record['shells']:
                self.assertIn(f'**S{n}**', report)
                self.assertIn(data['shells'][str(n)]['wreath'], report)
            self.assertNotIn('Apex Seed', report)

    def test_all_three_wreaths_exact_members_not_contiguous_ranges(self):
        data = source('shell_registry.json')
        self.assertEqual(len(data['wreaths']), 3)
        for record in data['wreaths'].values():
            report = shells.query_superphase(record['name'])
            self.assertIn(record['quality'], report)
            self.assertIn(str(record['shells']), report)
            for n in record['shells']:
                self.assertIn(f'- S{n}:', report)
        for alias, code in [(' sulfur ', 'Su'), ('MERCURY', 'Me'), ('salt', 'Sa')]:
            self.assertIn(f'({code})', shells.query_superphase(alias))
        self.assertIn('Unknown', shells.query_superphase('undeclared'))

    def test_bounds_and_input_types_do_not_raise_or_truncate(self):
        for query, limit in [(shells.query_shell, 36), (shells.query_archetype, 12),
                             (shells.read_hologram_chapter, 27)]:
            for value in [0, -1, limit + 1, True, False, 1.0, 1.9, float('nan'),
                          None, [], {}, '1.0', '١', '9' * 5000]:
                with self.subTest(query=query.__name__, value=repr(value)[:30]):
                    self.assertIn('Invalid', query(value))
            self.assertNotIn('Invalid', query(' 01 '))
            self.assertNotIn('Invalid', query('0' * 5000 + '1'))
            self.assertIn('Invalid', query('0' * 5000))
        for value in [None, [], 1, True, '', '   ']:
            self.assertIn('Invalid', shells.query_superphase(value))

    def test_source_catalog_conflicts_and_missing_records_hold(self):
        original = source('shell_registry.json')
        mutations = [lambda d: d.pop('shells'),
                     lambda d: d.update(shells=[]),
                     lambda d: d.update(shells=None),
                     lambda d: d.pop('archetypes'),
                     lambda d: d.update(wreaths=None),
                     lambda d: d['shells'].pop('36'),
                     lambda d: d['archetypes']['1']['shells'].append(4),
                     lambda d: d['wreaths']['1']['shells'].remove(1),
                     lambda d: d['shells']['1'].update(archetype='Fabricated'),
                     lambda d: d['shells']['1']['faces']['S'].update(address='Xi108:W2:A1:S1:S'),
                     lambda d: d['shells']['1'].pop('element_primary'),
                     lambda d: d['shells']['1'].update(faces=list(d['meta']['faces'])),
                     lambda d: d['shells']['1']['faces'].update(S=None),
                     lambda d: d['shells']['1']['faces'].update(S=[]),
                     lambda d: d['shells']['1'].update(shell_id=True),
                     lambda d: d['archetypes']['1']['shells'].append(1)]
        for mutate in mutations:
            data = copy.deepcopy(original)
            mutate(data)
            with patch.object(shells, '_shells', Mock(load=Mock(return_value=data))):
                for query, arg in [(shells.query_shell, 1), (shells.query_archetype, 1),
                                   (shells.query_superphase, 'Su')]:
                    report = query(arg)
                    self.assertTrue(report.startswith('HOLD:'), report)
                    self.assertNotIn('##', report)

    def test_all_27_hologram_chapters_match_source_ids_after_reordering(self):
        data = source('hologram_chapters.json')
        self.assertEqual(len(data['chapters']), 27)
        data['chapters'].reverse()
        with patch.object(shells, '_hologram', Mock(load=Mock(return_value=data))):
            for record in data['chapters']:
                report = shells.read_hologram_chapter(record['id'])
                self.assertIn(f"Chapter {record['id']}: {record['name']}", report)
                self.assertIn(record['description'], report)
                self.assertIn(data['mirror_law'], report)
                self.assertIn('HOLD', report)
                self.assertNotIn('**Earth Invariant**', report)

    def test_missing_duplicate_and_incomplete_chapters_hold(self):
        original = source('hologram_chapters.json')
        for mutate in [lambda d: d['chapters'].pop(),
                       lambda d: d['chapters'].append(d['chapters'][0]),
                       lambda d: d['chapters'][0].pop('description'),
                       lambda d: d.pop('mirror_law')]:
            data = copy.deepcopy(original)
            mutate(data)
            with patch.object(shells, '_hologram', Mock(load=Mock(return_value=data))):
                self.assertTrue(shells.read_hologram_chapter(1).startswith('HOLD:'))

    def test_valid_legacy_shell_and_catalog_paths_remain(self):
        shell = dict(number=1, archetype_name='Apex Seed', nodes=3, cumulative=3,
                     wreath='Su', archetype_index=1, mirror=36, dimension_first=3, action='seed')
        data = dict(shells=[shell], wreaths={'sulfur': dict(code='Su', function='ignite',
                    shells=[1], node_count=3, superphase='initial')})
        with patch.object(shells, '_shells', Mock(load=Mock(return_value=data))):
            self.assertIn('**Nodes**: 3', shells.query_shell(1))
            self.assertIn('Apex Seed', shells.query_archetype(1))
            self.assertIn('**Node Count**: 3', shells.query_superphase('Su'))
            self.assertNotIn('HOLD', shells.query_shell(1))
        data = dict(chapters=[dict(chapter=1, title='Legacy', summary='summary',
                    key_concepts=['concept'], earth_invariant='earth')],
                    meta=dict(four_projections=['S'], shared_invariants='shared'))
        with patch.object(shells, '_hologram', Mock(load=Mock(return_value=data))):
            self.assertIn('**Earth Invariant**: earth', shells.read_hologram_chapter(1))
            self.assertIn('Must be 1-21', shells.read_hologram_chapter(22))


if __name__ == '__main__':
    unittest.main()
