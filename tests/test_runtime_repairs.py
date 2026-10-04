"""Focused regressions; no corpus training or repository data writes."""
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))
from crystal_108d import meta_loop_engine as module
from crystal_108d.momentum_field import MomentumField
from crystal_108d._cache import JsonCache


class RuntimeRepairTests(unittest.TestCase):
    def test_command_entrypoints_compile(self):
        for name in ("command_spine.py", "command_membrane.py"):
            path = ROOT / "self_actualize/runtime" / name
            compile(path.read_bytes(), str(path), "exec")

    def wave(self, score):
        momentum = MomentumField()
        engine = Mock()
        engine.forward.return_value = SimpleNamespace(query=SimpleNamespace(home_shell=12), resonance=0.4)
        trainer = module.MetaLoopEngine(engine, momentum)
        trainer.loss = Mock()
        trainer.loss.observe.return_value = SimpleNamespace(total_score=score)
        trainer.loss.compute_all_gradients.return_value = dict.fromkeys(module.FACES, 0.5)
        return trainer, momentum

    def test_rejected_holographic_update_restores_every_parameter(self):
        trainer, momentum = self.wave(0.09)
        before = momentum.snapshot()
        with patch.object(module, 'update_edge_weights') as feedback:
            result = trainer.run_wave_holographic(0, ['probe'], 'A', 'S', 0.03)
        self.assertEqual(momentum.snapshot(), before)
        self.assertEqual((result.kept, result.discarded), (0, 1))
        self.assertEqual(result.momentum_deltas, dict.fromkeys(module.FACES, 0.0))
        feedback.assert_not_called()

    def test_accepted_boundary_update_keeps_momentum_and_water_lock(self):
        trainer, momentum = self.wave(0.1)
        before = momentum.snapshot()
        with patch.object(module, '_forward_result_to_feedback_input', return_value={}), patch.object(module, 'update_edge_weights') as feedback:
            result = trainer.run_wave_holographic(0, ['probe'], 'A', 'S', 0.03)
        self.assertNotEqual(momentum.snapshot(), before)
        self.assertEqual(momentum.snapshot().shell_momenta['C'], before.shell_momenta['C'])
        self.assertEqual((result.kept, result.discarded), (1, 0))
        feedback.assert_called_once_with({})

    def run_stubbed_cycle(self, cache):
        momentum = Mock()
        momentum.summary.return_value = {}
        momentum.hologram_16.return_value = {}
        engine = SimpleNamespace(doc_registry=[])
        trainer = module.MetaLoopEngine(engine, momentum)
        trainer.run_abcd_plus = Mock(return_value=SimpleNamespace(total_waves=0, elapsed_seconds=0))
        with patch.object(module, '_GRAPH_CACHE', cache), patch('crystal_108d.conservation_watchdog.run_watchdog'):
            trainer.run(module.MetaLoopConfig(depth=1))

    def test_graph_updates_persist_and_reconstruct_in_new_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = JsonCache('repair-test.json')
            cache._path = Path(directory) / 'graph.json'
            cache._qshr_path = cache._path.with_suffix('.qshr')
            cache._data = {'edges': [{'weight': 0.75}]}
            # Real atomic JSON/lock path; compression and sidecars are independent.
            with patch.object(JsonCache, 'compress', return_value=None), patch('crystal_108d._pheromone.PheromoneTrail.emit'):
                self.run_stubbed_cycle(cache)
            cold = JsonCache('repair-cold.json')
            cold._path = cache._path
            cold._qshr_path = cache._qshr_path
            self.assertEqual(cold.load(), {'edges': [{'weight': 0.75}]})

    def test_graph_save_failure_is_observable(self):
        cache = Mock()
        cache.save.side_effect = OSError('read-only fixture')
        with self.assertLogs(module.__name__, level='WARNING') as logs:
            self.run_stubbed_cycle(cache)
        self.assertIn('read-only fixture', logs.output[0])

    def test_legacy_zlib_and_framed_qshr_cache_readers(self):
        import json
        import zlib
        from crystal_108d.qshrink_pipeline import compress_json
        data = {'edges': [{'weight': 0.75}]}
        with tempfile.TemporaryDirectory() as directory:
            cache = JsonCache('legacy-reader-test.json')
            cache._path = Path(directory) / 'graph.json'
            cache._qshr_path = cache._path.with_suffix('.qshr')
            for payload in (zlib.compress(json.dumps(data).encode()), compress_json(data)):
                cache._qshr_path.write_bytes(payload)
                cache.reset()
                self.assertEqual(cache.load(), data)
            valid = zlib.compress(json.dumps(data).encode())
            for bad in (valid[:-1], valid + b'trailing', b'QSHRbroken', zlib.compress(b'7')):
                cache._qshr_path.write_bytes(bad)
                cache.reset()
                with self.assertRaises((ValueError, zlib.error)):
                    cache.load()

    def test_real_native_single_wave_with_synthetic_documents(self):
        from crystal_108d.geometric_forward import GeometricEngine
        momentum = MomentumField()
        docs = [{'id': 'synthetic-a', 'name': 'crystal structure', 'element': 'Earth',
                 'tokens': ['crystal', 'structure'], 'seed_vector': [1.0, 0.0, 0.0, 0.0]},
                {'id': 'synthetic-b', 'name': 'water flow', 'element': 'Water',
                 'tokens': ['water', 'flow'], 'seed_vector': [0.0, 0.0, 1.0, 0.0]}]
        engine = GeometricEngine(momentum, docs)
        trainer = module.MetaLoopEngine(engine, momentum)
        with patch.object(module, 'update_edge_weights'):
            result = trainer.run_wave_holographic(0, ['crystal structure'], 'A', 'S', 0.03)
        self.assertEqual(result.queries_run, 1)
        self.assertEqual(result.kept + result.discarded, 1)
        self.assertTrue(all(v == 0.5 for v in momentum.snapshot().shell_momenta['C'].values()))

    def test_current_v2_registries_have_working_source_bound_consumers(self):
        from crystal_108d.dimensions import resolve_dimensional_body, dimensional_lift, query_containment
        from crystal_108d.organs import query_organ
        from crystal_108d.live_lock import compute_live_lock
        self.assertIn('4D Kernel', resolve_dimensional_body(4))
        self.assertIn('G1_hologram', resolve_dimensional_body(4))
        self.assertIn('not found', resolve_dimensional_body(5))
        self.assertIn('6D Selector', dimensional_lift(4, 6))
        self.assertIn('HOLD', dimensional_lift(4, 6))
        self.assertIn('HOLD', query_containment(4))
        self.assertIn('Seed Vault', query_organ('O01'))
        self.assertIn('Shell range: 1-3', query_organ('Seed Vault'))
        self.assertIn('Omega Point', query_organ('all'))
        self.assertIn('HOLD', query_organ('1'))
        self.assertIn('not found', query_organ('missing-source'))
        self.assertIn('HOLD', compute_live_lock('5', '28'))
        self.assertIn('Active locks: 0', compute_live_lock('5', '28'))

    def test_runtime_dependencies_match_supported_import_api(self):
        import tomllib
        from packaging.requirements import Requirement
        from importlib.metadata import version
        from mcp.server.fastmcp import FastMCP
        metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
        dependencies = {r.name: r for r in map(Requirement, metadata['project']['dependencies'])}
        self.assertIn('1.26.0', dependencies['mcp'].specifier)
        self.assertNotIn('2.0.0', dependencies['mcp'].specifier)
        self.assertIn(version('mcp'), dependencies['mcp'].specifier)
        self.assertIn('numpy', dependencies)
        self.assertTrue(callable(FastMCP))

    def test_supported_requirements_install_matches_runtime_metadata(self):
        import tomllib
        from packaging.requirements import Requirement
        metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
        expected = {r.name: r for r in map(Requirement, metadata['project']['dependencies'])}
        lines = (ROOT / 'MCP/requirements.txt').read_text(encoding='utf-8').splitlines()
        requirements = {r.name: r for r in map(Requirement, (line for line in lines if line.strip() and not line.startswith('#')))}
        self.assertEqual(set(requirements), set(expected))
        for name in expected:
            self.assertEqual(requirements[name].specifier, expected[name].specifier)
            self.assertEqual(requirements[name].extras, expected[name].extras)
        self.assertNotIn('2.0.0', requirements['mcp'].specifier)

    def test_legacy_graph_decoding_does_not_import_numeric_pipeline(self):
        import json
        import zlib
        # A cold interpreter blocks numpy so installed desktop extras cannot
        # conceal an eager dependency in the legacy stdlib decoding path.
        import subprocess
        code = r"""
import importlib.abc, sys, tempfile, zlib, json
from pathlib import Path
class BlockNumpy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'numpy' or fullname.startswith('numpy.'):
            raise ModuleNotFoundError('numpy deliberately unavailable')
sys.meta_path.insert(0, BlockNumpy())
sys.path.insert(0, 'MCP')
from crystal_108d._cache import JsonCache
with tempfile.TemporaryDirectory() as directory:
    cache = JsonCache('fixture.json')
    cache._path = Path(directory) / 'fixture.json'
    cache._qshr_path = cache._path.with_suffix('.qshr')
    cache._qshr_path.write_bytes(zlib.compress(json.dumps({'shards': []}).encode()))
    assert cache.load() == {'shards': []}
assert 'numpy' not in sys.modules
print('cold stdlib legacy decode OK')
"""
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('cold stdlib legacy decode OK', result.stdout)

    def test_native_launcher_preflight_does_not_start_training(self):
        spec = importlib.util.spec_from_file_location('training_launcher', ROOT / 'run_full_training.py')
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        with patch.object(module, 'MetaLoopEngine') as trainer:
            self.assertEqual(launcher.main(['--check']), 0)
            trainer.assert_not_called()
        for value in ('0', '-1', 'nan', 'inf'):
            with self.assertRaises(SystemExit):
                launcher.main(['--max-time-minutes', value])


if __name__ == '__main__':
    unittest.main()
