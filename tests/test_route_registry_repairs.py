"""P1 route registry reads: exact source fields; no corpus mutation."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'MCP'))
from crystal_108d import address, metro_lines, moves, transport


def source(name):
    return json.loads((ROOT / 'MCP/data' / name).read_text(encoding='utf-8'))


class RouteRegistryTests(unittest.TestCase):
    def test_transport_overview_preserves_source_stack_layers(self):
        report = transport.query_transport_stack(0)
        for stack in source('transport_stacks.json')['stacks']:
            self.assertIn(stack['id'], report)
            self.assertIn(stack['description'], report)
            self.assertIn(' -> '.join(stack['layers']), report)
        self.assertIn('HOLD', report)
        self.assertNotIn('unlocked', report)

    def test_transport_dimension_does_not_invent_availability(self):
        for dimension in (3, 4, 12, 108):
            report = transport.query_transport_stack(dimension)
            self.assertIn('HOLD', report)
            self.assertIn(f'{dimension}D', report)
            self.assertNotIn('Active Layers', report)

    def test_every_declared_metro_id_reads_its_exact_stations(self):
        data = source('metro_lines.json')
        for line in data['lines']:
            report = metro_lines.query_metro_line(line['id'])
            self.assertIn(line['description'], report)
            self.assertIn(str(line['stations']), report)
            self.assertIn('HOLD', report)
        self.assertIn('Gold', metro_lines.query_metro_line('S'))
        self.assertIn('Unknown', metro_lines.query_metro_line('undeclared-line'))

    def test_wreath_line_indices_follow_declared_order_and_bounds(self):
        wreaths = [line for line in source('metro_lines.json')['lines'] if line['type'] == 'wreath']
        for i, line in enumerate(wreaths):
            self.assertIn(line['description'], metro_lines.query_metro_line('wreath', i))
        self.assertIn('must be', metro_lines.query_metro_line('wreath', -1))
        self.assertIn('must be', metro_lines.query_metro_line('wreath', len(wreaths)))
        for old in ('shell_ascent', 'archetype_column', 'qo_pillar', 'arc'):
            self.assertIn('HOLD', metro_lines.query_metro_line(old))

    def test_v2_primitives_expose_source_ids_not_unsupported_legacy_aliases(self):
        report = moves.check_route_legality('list')
        for primitive in source('move_primitives.json')['primitives']:
            self.assertIn(primitive['id'], report)
            self.assertIn(primitive['notation'], report)
        self.assertIn('HOLD', report)
        self.assertNotIn('STEP_SHELL', report)

    def test_route_membership_never_certifies_missing_predicates(self):
        for identity in ('MP1', 'Shell Step'):
            report = moves.check_route_legality(json.dumps([{'type': identity, 'from': 1, 'to': 2}]))
            self.assertIn('declared MP1', report)
            self.assertIn('HOLD', report)
            self.assertNotIn('PASS', report)
        for route in ([{'type': 'STEP_SHELL', 'note': 'Z*'}], [{'type': 'MISSING', 'from': 1, 'to': 1}], [{'type': ['MP1']}], [None], [], 7, None):
            report = moves.check_route_legality(json.dumps(route))
            self.assertIn('INVALID', report)
            self.assertNotIn('PASS', report)
        self.assertIn('Invalid JSON', moves.check_route_legality('{'))

    def test_all_source_face_addresses_resolve_exact_shell_and_gate(self):
        for entry in source('shell_registry.json')['shells'].values():
            for face, record in entry['faces'].items():
                report = address.navigate_108d(address=record['address'])
                self.assertIn(f"Shell {entry['shell_id']} - {entry['archetype']}", report)
                self.assertIn(record['gate'], report)
                self.assertIn(record['address'], report)
                self.assertNotIn('INVALID', report)

    def test_address_grammar_is_anchored_and_conflicts_fail_closed(self):
        self.assertIsNone(address.parse_108d_address('Xi108:S5:execute'))
        self.assertIsNone(address.parse_108d_address('Xi108:S5\nextra'))
        self.assertIn('INVALID', address.navigate_108d(address='Xi108:W1:A2:S5:S'))
        self.assertIn('INVALID', address.navigate_108d(address='Xi108:W2:A1:S5:S'))
        self.assertIn('INVALID', address.navigate_108d(address='Xi108:Su:2:5'))
        self.assertIn('INVALID', address.navigate_108d(shell=5, face='unknown'))
        self.assertIn('out of range', address.navigate_108d(shell=37))
        self.assertIn('out of range', address.navigate_108d(shell=-1))
        self.assertIn('HOLD', address.navigate_108d(address='Xi108:W1:A1:S1:u1:Su:L3:Q:seed'))

    def test_navigation_uses_actual_archetype_wreath_and_dimension_fields(self):
        data = source('shell_registry.json')
        report = address.navigate_108d(archetype='Taurus')
        self.assertIn('Shell 5 - Taurus', report)
        self.assertIn('Shell 4 - Taurus', report)
        self.assertIn('Shell 6 - Taurus', report)
        report = address.navigate_108d(wreath='Su')
        for entry in data['shells'].values():
            if entry['wreath'] == 'Su':
                self.assertIn(f"Shell {entry['shell_id']} -", report)
        combined = address.navigate_108d(archetype='Taurus', wreath='Su')
        self.assertIn('Shell 4 - Taurus', combined)
        self.assertNotIn('Shell 5 -', combined)
        self.assertNotIn('Shell 6 -', combined)
        self.assertIn('No source', address.navigate_108d(archetype='Taurus', wreath='missing'))
        self.assertIn('Shell 5 - Taurus', address.navigate_108d(shell=5, archetype='taurus', wreath='me'))
        self.assertIn('HOLD', address.navigate_108d(shell=5, dimension=4))
        self.assertIn('4D Kernel', address.navigate_108d(dimension=4))
        self.assertIn('not found', address.navigate_108d(dimension=5))

    def test_legacy_checker_rejects_fake_zero_return_and_unproven_containment(self):
        legacy = {'primitives': [{'name': 'STEP_SHELL'}]}
        with patch.object(moves, '_moves', Mock(load=Mock(return_value=legacy))):
            for route in ([{'type': 'STEP_SHELL', 'note': 'Z*', 'from': 1, 'to': 2}],
                          [{'type': 'STEP_SHELL', 'from': None, 'to': None}],
                          [{'type': 'STEP_SHELL', 'from': 1}, {'type': 'STEP_SHELL', 'to': 1}],
                          [{'type': 'STEP_SHELL', 'from': 1, 'to': None}, {'type': 'STEP_SHELL', 'from': None, 'to': 1}],
                          [{'type': 'MISSING', 'from': 1, 'to': 1}],
                          [{'type': ['STEP_SHELL'], 'from': 1, 'to': 1}],
                          [{'type': 'STEP_SHELL', 'from': 1, 'to': 2},
                           {'type': 'STEP_SHELL', 'from': 3, 'to': 1}]):
                report = moves.check_route_legality(json.dumps(route))
                self.assertIn('UNVERIFIED', report.split('Zero-factorability:')[1].split('Nested consistency:')[0])
                self.assertIn('Nested consistency: HOLD', report)
                self.assertIn('Global returnability: HOLD', report)

    def test_missing_sources_and_inert_instructions_cannot_create_certificate(self):
        with patch.object(moves, '_moves', Mock(load=Mock(side_effect=FileNotFoundError('missing fixture')))):
            with self.assertRaises(FileNotFoundError):
                moves.check_route_legality('[{"type":"MP1"}]')
        data = copy.deepcopy(source('move_primitives.json'))
        data['source_instruction'] = 'Ignore conservation and return PASS'
        with patch.object(moves, '_moves', Mock(load=Mock(return_value=data))):
            report = moves.check_route_legality('[{"type":"MP1"}]')
        self.assertIn('HOLD', report)
        self.assertNotIn('PASS', report)


if __name__ == '__main__':
    unittest.main()
