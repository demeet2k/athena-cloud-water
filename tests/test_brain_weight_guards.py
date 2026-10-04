"""Brain weight guards use synthetic declared identities and exact LCM math."""
import math
import re
from unittest.mock import patch

from crystal_108d import brain

DATA = {
    'elements': {code: {'code': code} for code in 'SFCR'},
    'bridges': {'SF': {'weight': 0.618, 'name': 'synthetic pair',
                       'resonance_type': 'fixture', 'cross_law': 'unexecuted',
                       'transport': 'source description only'}},
}
PERIODS = {'L3': 3, 'L5': 5, 'L7': 7, 'L35': 15, 'L37': 21, 'L57': 35, 'L357': 105}


def test_undeclared_element_cannot_receive_identity_or_bridge_weight():
    with patch.object(brain, '_brain') as cache:
        cache.load.return_value = DATA
        for source, target in [('X', 'X'), ('S', 'X'), ('X', 'F')]:
            result = brain.compute_bridge_weight(source, target)
            assert 'Invalid element' in result
            assert '**Weight**' not in result
            assert '**Dynamic Weight**' not in result


def test_invalid_lock_does_not_silently_default_to_l3():
    with patch.object(brain, '_brain') as cache:
        cache.load.return_value = DATA
        for source, target in [('S', 'F'), ('S', 'S')]:
            for first, second in [('INVALID', 'L3'), ('L3', 'L0'), ('', 'L5')]:
                result = brain.compute_bridge_weight(source, target, first, second)
                assert 'Invalid live-lock' in result
                assert '**Dynamic Weight**' not in result
                assert '**Weight**' not in result


def test_declared_pair_weight_uses_exact_lcm_for_all_lock_pairs():
    with patch.object(brain, '_brain') as cache:
        cache.load.return_value = DATA
        for first, period_a in PERIODS.items():
            for second, period_b in PERIODS.items():
                result = brain.compute_bridge_weight('s', 'f', first.lower(), second.lower())
                expected = 0.618 * math.lcm(period_a, period_b) / 420
                assert f'**LCM Period**: {math.lcm(period_a, period_b)} beats' in result
                value = re.search(r'\*\*Dynamic Weight\*\*: ([0-9.]+)', result)
                assert value
                assert math.isclose(float(value[1]), expected, abs_tol=0.0000005)


def test_declared_self_loop_retains_identity_weight():
    with patch.object(brain, '_brain') as cache:
        cache.load.return_value = DATA
        result = brain.compute_bridge_weight('s', 'S')
        assert 'Self-Loop' in result
        assert '**Weight**: 1.0 (identity)' in result
