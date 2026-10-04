"""Repository identity checks; no servers or external effects are started."""
from pathlib import Path
import os
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY = 'demeet2k/athena-cloud-water'
ORIGINAL_BASE_COMMIT = 'a7fcf26683c08f090cf94b14a8aa861db599c679'
KNOWN_REPOSITORIES = (
    'demeet2k/athena-cloud-water',
    'demeet2k/athena-flower-fire',
    'demeet2k/athena-fractal-air',
    'demeet2k/athena-square-earth',
)

def scalar(text, name):
    matches = re.findall(r'^' + re.escape(name) + r':\s*(.*?)\s*$', text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('Expected exactly one scalar: ' + name)
    return matches[0].split(' #', 1)[0].strip().strip('"')

def validate_identity(text, expected):
    if scalar(text, 'node_id') != expected:
        raise ValueError('node_id does not match the trusted repository identity')
    if scalar(text, 'github_repo') != 'https://github.com/' + expected:
        raise ValueError('github_repo does not match the trusted repository identity')

class RepositoryIdentityTests(unittest.TestCase):
    def test_identity_matches_external_repository(self):
        observed = os.environ.get('GITHUB_REPOSITORY')
        if observed is None:
            remote = subprocess.check_output(['git', '-C', str(ROOT), 'remote', 'get-url', 'origin'], text=True).strip()
            prefix = 'https://github.com/'
            self.assertTrue(remote.startswith(prefix), remote)
            observed = remote[len(prefix):].removesuffix('.git')
        self.assertEqual(observed, EXPECTED_REPOSITORY)
        validate_identity((ROOT / 'node.yaml').read_text(encoding='utf-8-sig'), observed)

    def test_repository_qualified_ids_are_distinct(self):
        self.assertEqual(len(KNOWN_REPOSITORIES), len(set(KNOWN_REPOSITORIES)))
        self.assertIn(EXPECTED_REPOSITORY, KNOWN_REPOSITORIES)
        self.assertRegex(ORIGINAL_BASE_COMMIT, r'^[0-9a-f]{40}$')
        self.assertNotEqual(EXPECTED_REPOSITORY, 'athena-mcp-server')

    def test_inherited_configuration_is_preserved(self):
        text = (ROOT / 'node.yaml').read_text(encoding='utf-8-sig')
        self.assertEqual(scalar(text, 'role'), 'unified')
        self.assertEqual(scalar(text, 'medium_class'), 'code')
        self.assertEqual(scalar(text, 'lobe_affinity'), 'null')

    def test_duplicate_upstream_and_wrong_url_are_rejected(self):
        text = (ROOT / 'node.yaml').read_text(encoding='utf-8-sig')
        for invalid in (
            re.sub(r'^node_id:.*$', 'node_id: athena-mcp-server', text, flags=re.MULTILINE),
            re.sub(r'^github_repo:.*$', 'github_repo: "https://github.com/demeet2k/athena-mcp-server"', text, flags=re.MULTILINE),
        ):
            with self.assertRaises(ValueError):
                validate_identity(invalid, EXPECTED_REPOSITORY)

if __name__ == '__main__':
    unittest.main()
