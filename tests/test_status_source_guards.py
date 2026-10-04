"""Status is a source census, not a readiness certificate or graph execution."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'MCP'))
import crystal_108d

SOURCES = ['shell_registry.json','dimensional_ladder.json','organ_atlas.json',
           'live_lock_registry.json','clock_projections.json','conservation_laws.json',
           'stage_codes.json','dimensional_emergence.json','metro_lines.json',
           'live_cell_constitution.json','hologram_chapters.json','node_registry.json']


def registry_sources():
    return {name: json.loads((ROOT/'MCP/data'/name).read_text(encoding='utf-8')) for name in SOURCES}


def caches(data):
    def factory(name):
        if name not in data:
            raise FileNotFoundError(name)
        return Mock(load=Mock(return_value=data[name]))
    return patch.object(crystal_108d, 'JsonCache', side_effect=factory)


class StatusSourceGuardTests(unittest.TestCase):
    def test_current_source_counts_ids_names_frontier_are_reported(self):
        data = registry_sources()
        with caches(data):
            report = crystal_108d.status_summary()
        self.assertIn('Source Census', report)
        self.assertIn('**Declared Frontier**: 6D', report)
        for filename, collection, id_key, name_key in [
                ('organ_atlas.json','organs','id','name'),
                ('conservation_laws.json','laws','id','name'),
                ('metro_lines.json','lines','id','name'),
                ('live_cell_constitution.json','requirements','id','name'),
                ('hologram_chapters.json','chapters','id','name')]:
            for record in data[filename][collection]:
                self.assertIn(f'{record[id_key]}: {record[name_key]}', report)
        for record in data['dimensional_ladder.json']['levels']:
            self.assertIn(f"{record['dimension']}: {record['name']}", report)
        for record in data['node_registry.json']['nodes']:
            self.assertIn(record['node_id'], report)
        for stage in data['stage_codes.json']['stages']:
            self.assertIn(stage, report)
        self.assertIn('declared cycle total 159; including FINAL 160', report)
        self.assertIn('**Emergence Transitions**: 6', report)
        self.assertIn('**Live-cell Requirement Descriptions**: 7', report)
        self.assertIn('**Metro Records**: 14', report)
        self.assertIn('**Source-record Locks**: 0', report)
        self.assertIn('HOLD', report)

    def test_v2_summary_omits_unsupported_readiness_and_legacy_claims(self):
        with caches(registry_sources()), patch.object(crystal_108d, '_mycelium_stats', side_effect=AssertionError('graph read')):
            report = crystal_108d.status_summary()
        for claim in ['16 stages', '7 phases', 'kernel embedding law', '6 schemas', '14-station metro',
                      '96-slot cockpit', 'Fisher-Rao', '810K', 'ALL PASS', 'Cert Class', 'RoundTripCertPack']:
            self.assertNotIn(claim, report)
        self.assertIn('do not verify node availability', report)
        self.assertNotIn('**Mycelium Graph**', report)

    def test_each_missing_source_holds_without_fallback_default_counts(self):
        original = registry_sources()
        for name in SOURCES:
            data = copy.deepcopy(original); del data[name]
            with caches(data):
                report = crystal_108d.status_summary()
            self.assertTrue(report.startswith('HOLD:'), report)
            self.assertNotIn('**Shells**', report)
            self.assertNotIn('Source Census', report)

    def test_each_source_malformed_root_metadata_and_unreadable_hold(self):
        original = registry_sources()
        for name in SOURCES:
            for bad in [None, [], {}, {'meta': None}, {'meta': []}]:
                data = dict(original); data[name] = bad
                with caches(data):
                    self.assertTrue(crystal_108d.status_summary().startswith('HOLD:'))
        for error in [PermissionError('read denied'), ValueError('invalid JSON')]:
            with patch.object(crystal_108d, 'JsonCache', return_value=Mock(load=Mock(side_effect=error))):
                self.assertTrue(crystal_108d.status_summary().startswith('HOLD:'))

    def test_conflicting_counts_catalogs_frontier_and_missing_ids_hold(self):
        original = registry_sources()
        mutations = [lambda d: d['shell_registry.json']['shells']['1'].update(faces=list(d['shell_registry.json']['meta']['faces'])),
                     lambda d: d['shell_registry.json']['shells']['1'].update(faces=None),
                     lambda d: d['shell_registry.json']['shells']['1']['faces'].update(S=None),
                     lambda d: d['shell_registry.json']['shells']['1']['faces'].update(S=[]),
                     lambda d: d['shell_registry.json']['shells'].update({'1': None}),
                     lambda d: d['shell_registry.json']['meta'].update(total_shells=666),
                     lambda d: d['organ_atlas.json']['meta'].update(total_organs=6),
                     lambda d: d['conservation_laws.json']['laws'][0].pop('statement'),
                     lambda d: d['shell_registry.json']['archetypes']['1']['shells'].append(4),
                     lambda d: d['dimensional_ladder.json'].update(current_frontier='999D'),
                     lambda d: d['dimensional_ladder.json']['levels'].append(d['dimensional_ladder.json']['levels'][0]),
                     lambda d: d['metro_lines.json']['lines'].pop(),
                     lambda d: d['live_cell_constitution.json']['requirements'][0].pop('name'),
                     lambda d: d['node_registry.json']['nodes'][0].pop('node_id'),
                     lambda d: d['hologram_chapters.json']['chapters'][0].update(id=999),
                     lambda d: d['metro_lines.json']['meta'].update(version='unknown'),
                     lambda d: d['live_cell_constitution.json']['meta'].update(version='unknown'),
                     lambda d: d['stage_codes.json']['stages'].pop('FINAL'),
                     lambda d: d['dimensional_emergence.json']['emergence_sequence'].pop(2)]
        for mutate in mutations:
            data = copy.deepcopy(original); mutate(data)
            with caches(data):
                self.assertTrue(crystal_108d.status_summary().startswith('HOLD:'))

    def test_unknown_or_mixed_core_versions_hold_without_legacy_defaults(self):
        original = registry_sources()
        for version in [None, 'unknown', '1.0']:
            data = copy.deepcopy(original)
            data['dimensional_ladder.json']['meta']['version'] = version
            with caches(data):
                self.assertTrue(crystal_108d.status_summary().startswith('HOLD:'))
        data = {name: {'meta': {'version':'unknown'}} for name in SOURCES[:6]}
        with caches(data):
            self.assertTrue(crystal_108d.status_summary().startswith('HOLD:'))

    def test_explicit_legacy_status_output_is_preserved(self):
        data = {name: {'meta': {'version':'1.0'}} for name in SOURCES[:6]}
        data['shell_registry.json']['meta'].update(total_shells=36,total_archetypes=12,total_wreaths=3,faces=['S','F','C','R'])
        data['organ_atlas.json']['meta']['total_organs'] = 6
        data['conservation_laws.json']['meta']['total_laws'] = 6
        with caches(data), patch.object(crystal_108d, '_mycelium_stats', return_value='legacy graph'):
            report = crystal_108d.status_summary()
        self.assertIn('16 stages', report)
        self.assertIn('7 phases', report)
        self.assertIn('legacy graph', report)
        self.assertNotIn('Source Census', report)


if __name__ == '__main__':
    unittest.main()
