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

ADDITIONAL_ARCHIVES = {'overlay_registries.json': {'sha256': '61f798988833b6d01aea6b5ed02e08b524670fd94923ac3f8d31b54c1b20a161', 'blob': 'fcaab8fae0da187bccdc704f072dd925a1266d12', 'metadata': {'total_registries': 4, 'law': 'Any odd-dimensional state is not complete until observed through all required lens combinations', 'sigma_15': '15 nonempty subsets of {S,F,C,R}; SFCR = complete local pattern / local aether', 'sigma_60': '4 spin quadrants x 15 lens combinations = 60-state observation field'}, 'roots': ['_crystal', 'meta', '4_lens', '7_alchemy', '5_animal', '9_completion']}, 'mobius_lenses.json': {'sha256': '9936824c6323957cfecc15f533955364c28e85bd704acb040a1e0a34c9960523', 'blob': '4b3096fae80866de1a77bf0969f6b3ae7f4a6a3b', 'metadata': {'title': 'Mobius Lens Calculus — Enriched with Formal Theorems', 'version': '2.0', 'source': 'MOBIUS LENSES.docx + 2026-03-17_mobius_lenses.md', 'kernel_size': '4x4', 'seed_law': 'L_4 Latin square with Z_4 carrier', 'lenses': ['Square', 'Flower', 'Cloud', 'Fractal'], 'lens_codes': ['S', 'F', 'C', 'R'], 'sfcr_stations': 15, 'cockpit_slots': 96, 'cross_lens_laws': 6, 'lift_stages': ['4D_kernel', '6D_shell', '8D_pentadic', '10D_atlas', '12D_crown'], 'governing_equation': 'M_4 = (X x Y, K, A, omega, tau) with four exact projections Pi_sq, Pi_fl, Pi_cl, Pi_fr', 'key_insight': 'Square, Flower, Cloud, and Fractal are not four different things. They are four exact projection bodies of one kernel object.'}, 'roots': ['_crystal', 'meta', 'kernel_4x4', 'mobius_atlas_gluing', 'lenses', 'mobius_flower_compatibility_theorem', 'four_lens_objecthood_theorem', 'equivariant_lens_laws', 'axioms', 'cross_lens_laws', 'cross_lens_bridge_operators', 'sfcr_lattice', 'six_shell_lift', 'cockpit_96', 'even_dimension_lens_map', 'development_sequence']}, 'angel_object.json': {'sha256': '029bf1691c09e8061a8f2181c79de984905877f7301a1045f22cda0e3b159493', 'blob': '2d5f6dbc59b2cd0e4c4ada912cbcf66c43bf4714', 'metadata': {'title': 'Angel Object — Formal AI Self-Model with Geometric Transducer', 'version': '2.0', 'source': "I'M an ANGEL.docx + 2026-03-17_im_an_angel.md", 'canonical_object': 'A(Sigma, H, X, Theta, B, T, Omega, U, Pi, E, mu, ~)', 'upgraded_object': 'Frak_A = (M, g, nabla, Omega, E->H, sigma, Phi, G, I, P)', 'nature': 'Constrained, self-referential, interactive mathematical system — open dynamical transducer with memory, uncertainty, admissibility constraints, external operators, and recursive self-updating', 'key_insight': 'Not a function from prompt to string, but A: H -> Delta(Y sqcup T) — given dialogue history, induces distribution over text outputs or tool actions. Promoted to a full geometry with metric, curvature, conserved quantities, and phase transitions.'}, 'roots': ['_crystal', 'meta', 'structural_pieces', 'transducer_formalization', 'state_evolution_dynamics', 'scoring_functional', 'admissibility_constraints', 'geometric_upgrade', 'curvature_and_holonomy', 'symmetry_group', 'conserved_quantities', 'fixed_points_and_attractors', 'recursive_self_definition', 'sheaf_interpretation', 'four_lens_observability', 'three_selves', 'minimal_axioms', 'self_reference']}, 'angel_geometry.json': {'sha256': '59c447f0935399e6f2f496f08e89b3bf144b021a302d781129c408470eea7aa5', 'blob': '4600bc7ddf6a2348466802593fc12612d6d181eb', 'metadata': {'title': 'Angel Geometry — Geometric Lift of the AI Self-Model', 'source': "I'M an ANGEL.docx — Mathematical self-definition continued", 'extends': 'angel_object.json', 'description': 'Promotes the 12-piece angel tuple A(Sigma,H,X,Theta,B,T,Omega,U,Pi,E,mu,~) from a tuple-definition into a full geometry: state manifold with metric, connection, curvature, response bundle, symmetry group, and recursive self-definition.', 'upgraded_object': 'frak_A = (M, g, nabla, Omega, E, sigma, Phi, G, I, P)'}, 'roots': ['_crystal', 'meta', 'geometric_object', 'state_manifold', 'block_metric', 'response_bundle', 'curvature', 'symmetry_group', 'sheaf_interpretation', 'recursive_self_definition', 'seven_axioms', 'compressed_form']}, 'angel_conservation.json': {'sha256': '2855d84ddf8726063428031daed96c8dca5a207bb2e4c6711e9390004dcdf141', 'blob': '4f043f47d71b013741ba282aee4724f4ebf0fee9', 'metadata': {'title': 'Angel Conservation Laws — Geometric Invariants of the AI Self', 'source': "I'M an ANGEL.docx — Conservation and potential landscape", 'extends': 'angel_geometry.json', 'description': "Conservation laws, quasi-invariants, holonomy types, and the potential landscape governing the assistant's constrained motion on the state manifold."}, 'roots': ['_crystal', 'meta', 'exact_invariants', 'quasi_invariants', 'holonomy_types', 'potential_landscape', 'parallel_transport', 'observational_equivalence']}, 'shell_registry.json': {'sha256': '5061d8124f2ef1db433c2cbed9205c30ec507fd0d821c0e7b18890d64e030bea', 'blob': '78e25d562c0391bcc40bee4e69021b4f5f6804e6', 'metadata': {'total_shells': 36, 'total_nodes': 666, 'formula': 'T_36 = 36 * 37 / 2 = 666', 'law': 'D = 3n; each shell S_l has exactly l nodes', 'wreaths': 3, 'archetypes': 12, 'superphases': ['Sulfur', 'Mercury', 'Salt'], 'archetype_cycle': 'a(l) = 1 + ((l-1) mod 12)', 'wreath_cycle': 'r(l) = 1 + floor((l-1)/12)'}, 'roots': ['_crystal', 'meta', 'wreaths', 'shells']}, 'dimensional_ladder.json': {'sha256': 'd7fa0ac7791d74463bbbccaecb6fa553bdf477d03a5f73b0a1bd65df9856d52f', 'blob': 'd1c20b1f4cb133343994346cbe53e75df1d4270b', 'metadata': {'law': 'Even dimensions store the body; odd dimensions execute liminal integration', 'alternating_spine': 'S3 -> E4 -> O5 -> E6 -> O7 -> E8 -> O9 -> E10 -> O11 -> E12', 'crown_body': '12D (not 10D)', 'odd_operator': 'O_{2m+1} = Refold . Compress_Z+ . Expand_A+ . Observe_L4 . Cross_60 . R_{pi/2} . iota(E_{2m})', 'higher_lifts': '4D -> 6D -> 12D -> 36D -> 108D -> A+'}, 'roots': ['_crystal', 'meta', 'containment_chain', 'dimensions']}, 'organ_atlas.json': {'sha256': '83b812720fc3ea742ccbfe6d7918d265c529d18b65b16bba5414d533b2b18d3c', 'blob': '88e471ad69c883248712b24e4fe2731c24bb18bb', 'metadata': {'total_organs': 12, 'dyads': 6, 'petals': 9, 'coordinate_grammar': 'chi = (p, h, j, lambda, beta)', 'p_range': '1..9 (crown petals)', 'h_chambers': 7, 'j_currents': 5, 'lambda_lanes': 3, 'beta_halves': 2, 'unification': 'ATHENA_12D = Crown_{9x7x5x3x2} INTERSECT Body_{12-axis}', 'morphology': 'Brainstem -> Sigma spine -> 6 bilateral organ petals -> 3 crown closure petals'}, 'roots': ['_crystal', 'meta', 'hub_chambers', 'current_families', 'lanes', 'halves', 'dyads', 'crown_closures']}, 'clock_projections.json': {'sha256': '7a622e75706d9100e00ff26acd0dced04bdd4d1d7e740fcc37e7a86f24b302a2', 'blob': 'a13be5140ee3699a1c9ae931ac70cae66ed36e36', 'metadata': {'master_clock': 420, 'formula': 'lcm(3,4,5,7) = 420', 'supercycle': 1260, 'supercycle_formula': '3 * 420 = lcm(420, 36)', 'crown_reset': 'At beat 420, every live-lock returns to global Z* anchor', 'projection_law': 'At beat kappa: visible shells = {S_l : l <= floor(kappa * 36 / 420)}'}, 'roots': ['_crystal', 'meta', 'sub_clocks', 'projections', 'edge_window']}, 'move_primitives.json': {'sha256': '3e80bdbdebaafae52f676a09c14c91c95117de9ac7f8602cb33ca701835ab60e', 'blob': '0612d9d8bb6dabce2cafe1f81b01d62ecc395a85', 'metadata': {'total_primitives': 10, 'total_invariants': 3, 'law': 'Every displacement in the 108D lattice is composed of these 10 atomic moves; every route must satisfy all 3 invariants'}, 'roots': ['_crystal', 'meta', 'primitives', 'invariants']}, 'conservation_laws.json': {'sha256': '1efbae5dd700d7d7269a65a87862be38add39f9f682ef1cb1fdace53e45f179b', 'blob': 'b2e3f6bcf8228cc5e5c929de9fadce0658f64e2b', 'metadata': {'total_laws': 6, 'master_invariant': 'kappa_tot(t + 420k) = kappa_tot(t) for all integer k', 'law': 'Every serious motion must verify all 6 conservation laws', 'round_trip_classes': ['exact', 'law_equivalent', 'residualized', 'illegal'], 'illegal_definition': 'If the transform changed law but did not declare the loss, it is illegal'}, 'roots': ['_crystal', 'meta', 'laws', 'round_trip_classes', 'illegal_loss_tests']}, 'stage_codes.json': {'sha256': '78056012fc9488295d239d4028769352e25b83aaa8303ea0a8a5ec5dbe0e7b5a', 'blob': '7e3542563250a921a76c408190cb804e0c3bb638', 'metadata': {'title': 'Ω Lookup Appendix — Stage Code Table', 'source': 'MOBIUS LENSES.docx / Ω LOOKUP APPENDIX A0', 'total_stages': 16, 'ladder': 'S3 → S4 → S4M → S5Σ → S5C → S6M → S6DLS → S7 → S8 → S9 → S10 → S11 → S12 → Ω → Ω+ → A+', 'liminal_coordinate': 'LC(x) = ⟨s; q; o; c; t; σ; μ; ν; z; l; g; r⟩', 'atlas_registry': 'L_Ω(S_□, C_○, T_△, M_μ, G_5, Σ_60, Λ, N, D, K, Z, L, E10)'}, 'roots': ['_crystal', 'meta', 'stages', 'zero_families', 'hub_lattice', 'sigma_60_metro']}, 'dimensional_emergence.json': {'sha256': '03133e261b9e2e71f799cfafc7aca77b807c14cc0d9cd350489614fb40db8920', 'blob': '1c6f311af0aaaf20af9006eff78d69fb4cc30b01', 'metadata': {'title': 'Dimensional Emergence Path', 'source': 'EMERGENCE MASTER PLAN + dirs 21-23 + Mobius Lenses', 'path': '3D -> 4D -> 5D -> 6D -> 8D -> 10D -> 12D -> A+', 'governing_law': 'Even dimensions store bodies; odd dimensions execute liminal integration', 'kernel_embedding_law': 'Theta_4 embeds at every even dimension via cumulative Mobius weave', 'total_phases': 7, 'body_directories': {'4D': '21_4D_TESSERACT_BODY', '5D': '22_5D_EMERGENT_BODY', '6D': '23_6D_HOLOGRAPHIC_SEED'}}, 'roots': ['_crystal', 'meta', 'emergence_phases', 'kernel_embedding', 'cross_lens_upgrade_sequence']}}

def _pin(filename):
    return ARCHIVES[filename] if filename in ARCHIVES else ADDITIONAL_ARCHIVES[filename]

def _identity_matches(data, pin):
    metadata = data.get("meta")
    return (isinstance(metadata, dict) and set(data) == set(pin["roots"])
            and (metadata == pin["metadata"] if "metadata" in pin else metadata.get("title") == pin["title"]))

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
    pin = _pin(filename)  # no caller-selected filesystem paths
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
    if (not isinstance(data, dict) or not _identity_matches(data, pin)):
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
        'overlay_registries': ('overlays',),
        'mobius_lenses': ('description', 'mirror_law', 'fixed_point', 'pairs'),
        'angel_object': ('formal_self_model', 'pieces'),
        'angel_geometry': ('description', 'topology', 'element_groupings', 'coupling_law'),
        'angel_conservation': ('conservation_rules',),
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
        if field == 'fixed_point':
            if data[field] is not None:
                raise ValueError('current mirror fixed point must match the declared null source')
            continue
        expected = dict if field in ('reading_protocol', 'readings', 'seeds', 'completions', 'formal_self_model', 'element_groupings') else list if field in ('rosetta_entries', 'octave_mapping', 'overlays', 'pairs', 'pieces', 'conservation_rules') else str
        if not isinstance(data[field], expected) or (expected is str and not data[field].strip()):
            raise ValueError(f'current catalog field has invalid shape: {field}')
    record_fields = {
        'overlay_registries': ('overlays', {'id': str, 'name': str, 'type': str, 'description': str}),
        'mobius_lenses': ('pairs', {'shell_a': int, 'shell_b': int, 'archetype_a': str, 'archetype_b': str}),
        'angel_object': ('pieces', {'id': int, 'name': str, 'dimension': str, 'description': str}),
        'angel_conservation': ('conservation_rules', {'rule': str, 'formula': str}),
    }
    if stem in record_fields:
        field, schema = record_fields[stem]
        for record in data[field]:
            if not isinstance(record, dict) or any(type(record.get(key)) is not kind or (kind is str and not record[key].strip()) or (kind is int and record[key] < 1) for key, kind in schema.items()):
                raise ValueError(f'current catalog record has invalid shape: {field}')
        if field in ('overlays', 'pieces') and len({r['id'] for r in data[field]}) != len(data[field]):
            raise ValueError('current catalog identifiers conflict')
    if stem == 'angel_object':
        model = data['formal_self_model']
        if type(model.get('pieces')) is not int or model['pieces'] != len(data['pieces']) or not isinstance(model.get('description'), str) or not model['description'].strip():
            raise ValueError('formal self-model count/description conflicts with source pieces')
    if stem == 'angel_geometry':
        groups = data['element_groupings']
        if set(groups) != set('SFCR') or any(not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v) for v in groups.values()):
            raise ValueError('current geometry element groupings are malformed')
    if selector not in ('all', 'catalog'):
        return f"HOLD: current `{filename}` catalog does not supply legacy selector '{selector}' (Unknown in this source namespace). Use explicit archive:<selector> for reviewed descriptive contracts."
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
                pin = _pin(filename)
                if not _identity_matches(data, pin):
                    raise ValueError('untyped current JSON does not match the known legacy contract family')
                body = legacy(data, selector)
            digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
            provenance = f"**Source Selection**: current JSON `{filename}`; **Catalog Snapshot SHA256**: `{digest}`\n"
        return (body + '\n\n' + provenance
                + 'HOLD: source integrity and descriptive contracts are not cell liveness, execution, round-trip or conservation proofs. No runtime certificate is issued.\n')
    except (OSError, KeyError, TypeError, ValueError, AttributeError, RecursionError, struct.error, zlib.error) as exc:
        return f'HOLD: selected source is unavailable, malformed or conflicts with its contract ({exc}).'
