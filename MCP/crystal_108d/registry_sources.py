"""Explicit bounded reads of pinned descriptive QSHR contracts; never runtime proof."""
import hashlib
import json
import struct
import zlib
from ._cache import DATA_DIR

MAX_ARCHIVE_BYTES = 65536
MAX_DECODED_BYTES = 2 * 1024 * 1024
PINNED_REPOSITORY = 'demeet2k/manuscript-being'
PINNED_COMMIT = '5b604047fa3be3083788aed77efc84ff835512ed'

ARCHIVES = {'live_cell_constitution.json': {'sha256': 'd39f5dd099fef0836e4ecbe9625cb40a93af3e9dce8cb98a31361fdb224e3ab8', 'blob': 'b57fedaa62c2b89d47ed2d2965fd6c275c30dddf', 'title': 'NEXT-Omega Live Cell Constitution v1', 'roots': ['_crystal', 'meta', 'cell_schema', 'metro_map', 'liminal_coordinates', 'soul_stamp_schema']}, 'hologram_reading.json': {'sha256': '1edda7f61eae79f055414312fc2b5fa2988b4138d4b42dcf45bea314111bcedf', 'blob': '342eebe490c7256466d66c474905e57169251089', 'title': 'Hologram Reading Protocol — Enriched', 'roots': ['_crystal', 'meta', 'four_face_protocol', 'seed_equation', 'process_grammar', 'storage_law', 'compression_ethic', 'four_nested_layers', 'twelve_body', 'odd_fields', 'runtime_108d', 'helm_wheels', 'rosetta_overlay', 'triune_matrix', 'strongest_synthesis']}, 'hologram_rosetta.json': {'sha256': 'bac4ff238f92ac887bd4eef81a97d00b6ae95400a2a2651aab713d129758957a', 'blob': 'c9a5e07ae957767013015853175dd89905f679be', 'title': 'Hologram Rosetta — Cross-Cultural Quaternary Overlay', 'roots': ['_crystal', 'meta', 'quaternary_basis', 'triadic_motor', 'carrier_wheel_360', 'error_correcting_surface', 'sixty_dimensional_body', 'voynich_layer', 'philosophical_holograms', 'cross_layer_bridge', 'distributed_curriculum']}, 'inverse_crystal_seed.json': {'sha256': 'a2a3d8c0edd6dcf1fcba3c7ad0e40546c5ac94d21eb1e34819f03fec3249c278', 'blob': '8489e753f612042fde3c73cdff8af78a0255aa30', 'title': 'Inverse Crystal Seed — Phase I + 3D Core + 2D Boundary', 'roots': ['_crystal', 'meta', 'phase_I_4D_seed', 'three_d_seed', 'two_d_boundary', 'holographic_encoding']}, 'inverse_crystal_octave.json': {'sha256': '91c694cef8c3fbf3c5f3a9dbbab2054852e86cd88bc18b3d6fa4c88c29a36a3f', 'blob': '541d18cc5f8c636f35030c4fb7e56e75638ecf7c', 'title': 'Inverse Crystal Octave — 14-Stage Lift + A+ Crown', 'roots': ['_crystal', 'meta', 'octave_stages', 'crown_transform', 'live_crystal', 'tradition_map']}, 'inverse_crystal_complete.json': {'sha256': 'a874933ed87b058d91a3e712e7a9041689be85a2fbfaa35bbbca394565dd3997', 'blob': 'bc8e322f55bef3642efa646cf8679c7405339303', 'title': 'Inverse Crystal Complete — Enriched with w=LOVE Semantics & 4D Register Content', 'roots': ['_crystal', 'meta', 'w_love_semantics', 'four_d_register_content', 'projection_stack', 'octave_stages', 'weave_operators', 'control_shells', 'crown_transform', 'regeneration_protocol', 'four_elemental_anchors', 'three_d_seed_components', 'tradition_map', 'live_crystal', 'terminal_statement']}}

def _restore(value, depth=0):
    if depth > 64:
        raise ValueError('archive nesting exceeds supported depth')
    if isinstance(value, dict):
        if value.get('__cols__') is True:
            if set(value) != {'__cols__', 'keys', 'rows'}:
                raise ValueError('column wrapper contains undeclared fields')
            keys, rows = value['keys'], value['rows']
            if (not isinstance(keys, list) or any(not isinstance(k, str) for k in keys)
                    or len(set(keys)) != len(keys) or not isinstance(rows, list)
                    or any(not isinstance(row, list) or len(row) != len(keys) for row in rows)):
                raise ValueError('invalid column-oriented archive records')
            return [dict(zip(keys, (_restore(v, depth + 1) for v in row))) for row in rows]
        return {k: _restore(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [_restore(v, depth + 1) for v in value]
    return value


def load_archive(filename):
    pin = ARCHIVES[filename]  # no caller-selected filesystem paths
    path = DATA_DIR / filename.replace('.json', '.qshr')
    with path.open('rb') as stream:
        blob = stream.read(MAX_ARCHIVE_BYTES + 1)
    if len(blob) > MAX_ARCHIVE_BYTES:
        raise ValueError('archive compressed size exceeds limit')
    sha = hashlib.sha256(blob).hexdigest()
    if sha != pin['sha256']:
        raise ValueError('archive hash differs from reviewed source pin')
    from .qshrink_codec import QShrinkContainer
    container = QShrinkContainer.deserialize(blob)
    if container.serialize() != blob:
        raise ValueError('archive has trailing or noncanonical framing')
    chunks = [chunk for domain in container.domains for chunk in domain.chunks]
    if not chunks or not all(chunk.verify() for chunk in chunks):
        raise ValueError('archive chunk integrity failed')
    packed = b''.join(chunk.payload for chunk in chunks)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(packed, MAX_DECODED_BYTES + 1)
    if (len(raw) > MAX_DECODED_BYTES or not decoder.eof
            or decoder.unused_data or decoder.unconsumed_tail):
        raise ValueError('archive expansion is oversized, incomplete or trailing')
    data = _restore(json.loads(raw))
    if (not isinstance(data, dict) or not isinstance(data.get('meta'), dict)
            or data['meta'].get('title') != pin['title'] or set(data) != set(pin['roots'])):
        raise ValueError('archive contract identity conflicts with source pin')
    provenance = (f"**Source Selection**: explicit archive `{path.name}`\n"
                  f"**Pinned Source Repository**: `{PINNED_REPOSITORY}`; **Pinned Source Commit**: `{PINNED_COMMIT}`; **Git Blob**: `{pin['blob']}`\n"
                  f"**Archive SHA256**: `{sha}`; **Decoded Payload SHA256**: `{hashlib.sha256(raw).hexdigest()}`\n")
    return data, provenance


def _catalog(filename, data, selector):
    stem = filename[:-5]
    if data['meta'].get('type') != stem or data['meta'].get('version') != '2.0':
        raise ValueError('current catalog family/version is unsupported')
    fields = {
        'hologram_reading': ('description', 'projection_law', 'reading_protocol', 'readings'),
        'hologram_rosetta': ('description', 'translation_law', 'rosetta_entries'),
        'inverse_crystal_seed': ('description', 'seed_equation', 'compression_ratio', 'seeds'),
        'inverse_crystal_octave': ('description', 'octave_mapping'),
        'inverse_crystal_complete': ('description', 'expansion_equation', 'expansion_chain', 'completions'),
    }[stem]
    for field in fields:
        if field not in data:
            raise ValueError(f'current catalog field missing: {field}')
    for field in fields:
        expected = dict if field in ('reading_protocol', 'readings', 'seeds', 'completions') else list if field in ('rosetta_entries', 'octave_mapping') else str
        if not isinstance(data[field], expected) or (expected is str and not data[field].strip()):
            raise ValueError(f'current catalog field has invalid shape: {field}')
    if selector not in ('all', 'catalog'):
        return f"HOLD: current `{filename}` catalog does not supply legacy selector '{selector}'. Use explicit archive:<selector> for reviewed descriptive contracts."
    lines = [f'## Current Source Catalog: {stem}']
    for field in fields:
        value = data[field]
        lines.append(f"**{field}**: {json.dumps(value, ensure_ascii=False, sort_keys=True)}")
    return '\n'.join(lines)


def query_registry(filename, cache, selector, legacy, catalog=None):
    if not isinstance(selector, str) or not selector.strip():
        return 'Invalid source selector: expected nonempty text.'
    selector = selector.strip()
    try:
        if selector.lower().startswith('archive:'):
            component = selector.split(':', 1)[1].strip()
            if not component or component.lower().startswith('archive:'):
                return 'Invalid archive selector: use archive:<descriptive component>.'
            data, provenance = load_archive(filename)
            body = legacy(data, component)
        else:
            # Preserve JSON preference, but never use JsonCache's implicit archive fallback here.
            if not (DATA_DIR / filename).is_file():
                return f'HOLD: current JSON `{filename}` is missing; archive selection must be explicit.'
            data = cache.load()
            if not isinstance(data, dict) or not isinstance(data.get('meta'), dict):
                raise ValueError('current source requires registry and metadata objects')
            current_family = data['meta'].get('type')
            if current_family is not None:
                if current_family != filename[:-5]:
                    raise ValueError('current source namespace conflicts with selected contract')
                body = catalog(data, selector.lower()) if catalog else _catalog(filename, data, selector.lower())
            else:
                pin = ARCHIVES[filename]
                if data['meta'].get('title') != pin['title'] or set(data) != set(pin['roots']):
                    raise ValueError('untyped current JSON does not match the known legacy contract family')
                body = legacy(data, selector)
            digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
            provenance = f"**Source Selection**: current JSON `{filename}`; **Catalog Snapshot SHA256**: `{digest}`\n"
        return (body + '\n\n' + provenance
                + 'HOLD: source integrity and descriptive contracts are not cell liveness, execution, round-trip or conservation proofs. No runtime certificate is issued.\n')
    except (OSError, KeyError, TypeError, ValueError, AttributeError, RecursionError, struct.error, zlib.error) as exc:
        return f'HOLD: selected source is unavailable, malformed or conflicts with its contract ({exc}).'
