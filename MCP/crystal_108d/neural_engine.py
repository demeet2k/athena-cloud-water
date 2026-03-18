"""
Crystal Neural Engine — SFCR Forward Pass with Resonance/Desire/Action
========================================================================
An actual computation engine that routes queries through 4 SFCR processing
paths using crystal-internal weights, then merges via brain bridge weights.

Forward pass pipeline:
  QueryState Q → |S-path: gate weights|  → partial_S
               → |F-path: pair weights|  → partial_F  → Bridge merge → Ranked → CommitWitness
               → |C-path: neighbor idx|  → partial_C
               → |R-path: seed weights|  → partial_R

Implements for real:
  - ResonanceMetric R(X) = w1*AddrFit + w2*InvFit + w3*Phase + w4*Boundary + w5*Scale + w6*Compress
  - DesireField D_Q(X) = λ_a*Align + λ_e*Expl + λ_z*ZPA + λ_c*ConSat
  - Action A(Q,X) = K(X) - D_Q(X)  (minimize)
  - CommitWitness θ(X) = 4 gates (resonance ≥ τ, boundary, crossview, scale)
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .crystal_weights import (
    FractalWeightStore,
    get_store,
    ELEMENT_TO_FACE,
    FACE_TO_ELEMENT,
    PHI,
    PHI_INV,
)
from .constants import (
    TOTAL_SHELLS,
    ARCHETYPE_NAMES,
    LENS_CODES,
)

# Brain bridge resonance classes (from brain.py)
GOLDEN_BRIDGES = {"SF", "FC", "CR"}
NEUTRAL_BRIDGES = {"SC", "FR"}
DISTANT_BRIDGES = {"SR"}

BRIDGE_WEIGHTS = {
    "SF": PHI_INV,        # 0.618 — golden
    "FC": PHI_INV,        # 0.618 — golden
    "CR": PHI_INV,        # 0.618 — golden
    "SC": 0.500,          # neutral
    "FR": 0.500,          # neutral
    "SR": PHI_INV ** 2,   # 0.382 — distant
}


def _bridge_key(a: str, b: str) -> str:
    """Canonical bridge key in SFCR order."""
    order = {"S": 0, "F": 1, "C": 2, "R": 3}
    pair = sorted([a, b], key=lambda x: order.get(x, 9))
    return "".join(pair)


# ── Data structures ──────────────────────────────────────────────────


@dataclass
class QueryState:
    """The input to a forward pass — a query decomposed into crystal terms."""
    raw_query: str
    tokens: list[str] = field(default_factory=list)
    home_shell: int = 1
    home_face: str = "S"
    home_gate: str = "G00"
    matched_docs: list[str] = field(default_factory=list)
    depth: int = 1  # search depth


@dataclass
class CandidateScore:
    """Score for a single candidate document from a single SFCR path."""
    doc_id: str
    doc_name: str
    element: str
    gate: str
    shell: int
    score: float
    path: str  # which SFCR path produced this


@dataclass
class ForwardResult:
    """Complete result of a forward pass."""
    query: QueryState
    candidates: list[RankedCandidate] = field(default_factory=list)
    resonance: float = 0.0
    committed: bool = False
    commit_witness: Optional[CommitWitness] = None
    sfcr_scores: dict = field(default_factory=dict)  # path→{doc→score}
    elapsed_ms: float = 0.0
    cross_element_pairs_used: list[str] = field(default_factory=list)


@dataclass
class RankedCandidate:
    """A candidate ranked by action minimization."""
    doc_id: str
    doc_name: str
    element: str
    gate: str
    shell: int
    merged_score: float
    action: float        # K(X) - D_Q(X)
    resonance: float     # R(X)
    desire: float        # D_Q(X)
    path_contributions: dict = field(default_factory=dict)  # {"S": 0.3, "F": 0.8, ...}


@dataclass
class CommitWitness:
    """Four-gate commitment proof."""
    resonance_gate: bool    # R(X) ≥ threshold
    boundary_gate: bool     # within addressable crystal
    crossview_gate: bool    # consistent across SFCR lenses
    scale_gate: bool        # consistent across compression levels
    committed: bool = False
    address: str = ""
    timestamp: str = ""


# ── Resonance / Desire / Action computation ──────────────────────────


class ResonanceComputer:
    """Compute the 6-component ResonanceMetric R(X)."""

    @classmethod
    def compute(cls, query: QueryState, doc: dict, store: FractalWeightStore) -> float:
        """R(X) = Σ w_i * component_i — weights read from store (learnable)."""
        W = store.resonance_weights
        addr_fit = cls._addr_fit(query, doc, store)
        inv_fit = cls._inv_fit(query, doc)
        phase = cls._phase_fit(query, doc)
        boundary = cls._boundary_fit(doc)
        scale = cls._scale_fit(doc, store)
        compress = cls._compress_fit(doc, store)

        return (
            W["addr_fit"] * addr_fit
            + W["inv_fit"] * inv_fit
            + W["phase"] * phase
            + W["boundary"] * boundary
            + W["scale"] * scale
            + W["compress"] * compress
        )

    @staticmethod
    def _addr_fit(query: QueryState, doc: dict, store: FractalWeightStore) -> float:
        """How well the candidate's crystal address matches the query."""
        doc_shell = store.doc_to_shell(doc)
        shell_dist = abs(doc_shell - query.home_shell)
        # Closer shells → higher fit (normalized to [0,1])
        return max(0.0, 1.0 - shell_dist / TOTAL_SHELLS)

    @staticmethod
    def _inv_fit(query: QueryState, doc: dict) -> float:
        """Invariant fit: how many structural features overlap."""
        q_tokens = set(query.tokens)
        d_tokens = set(doc.get("tokens", []))
        if not q_tokens or not d_tokens:
            return 0.0
        jaccard = len(q_tokens & d_tokens) / len(q_tokens | d_tokens)
        return jaccard

    @staticmethod
    def _phase_fit(query: QueryState, doc: dict) -> float:
        """Phase alignment: same gate → high fit."""
        doc_gate = doc.get("gate", "G00")
        if doc_gate == query.home_gate:
            return 1.0
        # Gate distance (circular on G00-G15)
        q_num = int(query.home_gate[1:])
        d_num = int(doc_gate[1:])
        dist = min(abs(q_num - d_num), 16 - abs(q_num - d_num))
        return max(0.0, 1.0 - dist / 8)

    @staticmethod
    def _boundary_fit(doc: dict, query: "QueryState | None" = None,
                      liminal_coord: "LiminalCoordinate | None" = None) -> float:
        """Boundary: continuous distance from shell boundary + liminal region fit.

        Replaces the old binary check (has_element/has_gate/has_chapters → ~1.0
        for all curated docs) with a continuous signal that varies per query-doc pair.
        """
        # Component 1: Shell boundary distance (closer to boundary → lower fit)
        doc_shell = doc.get("_shell", 18)  # pre-computed or default to center
        # Distance from nearest archetype boundary (every 3 shells)
        boundary_dist = min(
            (doc_shell - 1) % 3,  # distance from lower archetype boundary
            3 - (doc_shell - 1) % 3,  # distance from upper archetype boundary
        )
        boundary_score = boundary_dist / 1.5  # normalize to [0, 1], center of archetype = 1.0

        # Component 2: Element diversity of the document's neighborhood
        doc_chapters = doc.get("chapters", [])
        doc_appendices = doc.get("appendices", [])
        structural_richness = min(1.0, (len(doc_chapters) + len(doc_appendices)) / 8.0)

        # Component 3: Liminal region fit (if observer provides coordinate)
        liminal_fit = 0.5  # neutral default
        if liminal_coord is not None:
            doc_element = doc.get("element", "Earth")
            from .crystal_weights import ELEMENT_TO_FACE
            doc_face = ELEMENT_TO_FACE.get(doc_element, "S")
            if doc_face in liminal_coord.active_elements:
                liminal_fit = 0.8  # doc is in observer's active element set
                lo, hi = liminal_coord.shell_range
                if lo <= doc_shell <= hi:
                    liminal_fit = 1.0  # doc is in observer's shell range too
            else:
                liminal_fit = 0.2  # doc outside observer's element focus

        return boundary_score * 0.4 + structural_richness * 0.3 + liminal_fit * 0.3

    @staticmethod
    def _scale_fit(doc: dict, store: FractalWeightStore) -> float:
        """Scale consistency: weight at full vs seed level agree."""
        shell = store.doc_to_shell(doc)
        seed = store.get_shell_seed(shell)
        if not seed:
            return 0.5  # no data → neutral
        decomp = store.decompress_from_seed(shell)
        error = decomp.get("reconstruction_error", 0.0)
        # Low error → high scale fit
        return max(0.0, 1.0 - error / max(seed.mean, 0.01))

    @staticmethod
    def _compress_fit(doc: dict, store: FractalWeightStore) -> float:
        """Compression quality: how well the seed represents this doc's shell."""
        shell = store.doc_to_shell(doc)
        seed = store.get_shell_seed(shell)
        if not seed or seed.std == 0:
            return 0.5
        # Lower relative std → better compression
        cv = seed.std / max(abs(seed.mean), 0.01)
        return max(0.0, 1.0 - cv)


class DesireComputer:
    """Compute the 4-term DesireField D_Q(X)."""

    @classmethod
    def compute(cls, query: QueryState, doc: dict, store: FractalWeightStore) -> float:
        """D_Q(X) = Σ λ_i * term_i — weights read from store (learnable)."""
        L = store.desire_weights
        align = cls._alignment(query, doc)
        explore = cls._exploration(doc, store)
        zpa = cls._zero_point_attraction(query, doc)
        con_sat = cls._constraint_satisfaction(query, doc)

        return (
            L["align"] * align
            + L["explore"] * explore
            + L["zpa"] * zpa
            + L["con_sat"] * con_sat
        )

    @staticmethod
    def _alignment(query: QueryState, doc: dict) -> float:
        """How well the candidate aligns with query intent."""
        q_tokens = set(query.tokens)
        d_tokens = set(doc.get("tokens", []))
        if not q_tokens:
            return 0.0
        # Recall: what fraction of query tokens appear in doc
        recall = len(q_tokens & d_tokens) / len(q_tokens)
        return recall

    @staticmethod
    def _exploration(doc: dict, store: FractalWeightStore) -> float:
        """Novelty bonus: docs in less-populated shells are more exploratory."""
        shell = store.doc_to_shell(doc)
        seed = store.get_shell_seed(shell)
        if not seed:
            return 1.0  # unknown → maximum exploration
        # Fewer entries → more exploration value
        max_count = max(s.count for s in store.shell_seeds.values()) if store.shell_seeds else 1
        return 1.0 - (seed.count / max(max_count, 1))

    @staticmethod
    def _zero_point_attraction(query: QueryState, doc: dict) -> float:
        """Attraction to convergence zones (Ch11, Ch18, Ch20, Ch21, AppF, AppG, AppI, AppM)."""
        zero_chapters = {"Ch11", "Ch18", "Ch20", "Ch21"}
        zero_appendices = {"AppF", "AppG", "AppI", "AppM"}

        doc_chapters = set(doc.get("chapters", []))
        doc_appendices = set(doc.get("appendices", []))

        ch_overlap = len(doc_chapters & zero_chapters) / max(len(zero_chapters), 1)
        app_overlap = len(doc_appendices & zero_appendices) / max(len(zero_appendices), 1)

        return (ch_overlap + app_overlap) / 2.0

    @staticmethod
    def _constraint_satisfaction(query: QueryState, doc: dict,
                                 archetype_role: "ArchetypeRole | None" = None) -> float:
        """Constraint satisfaction: continuous match between doc and query/role.

        Replaces the old binary check (has element/gate/chapters/tokens → ~1.0
        for all curated docs) with a continuous signal based on:
        1. Token overlap depth (not just presence)
        2. Element alignment with query
        3. Archetype role constraint match (if observer provides role)
        """
        # Component 1: Token depth — ratio of doc tokens to query tokens
        q_tokens = set(query.tokens) if query.tokens else set()
        d_tokens = set(doc.get("tokens", []))
        if q_tokens and d_tokens:
            recall = len(q_tokens & d_tokens) / len(q_tokens)
            precision = len(q_tokens & d_tokens) / len(d_tokens) if d_tokens else 0
            token_depth = 2 * recall * precision / max(recall + precision, 1e-10)
        else:
            token_depth = 0.0

        # Component 2: Element alignment — same element as query = higher satisfaction
        doc_element = doc.get("element", "")
        from .crystal_weights import ELEMENT_TO_FACE
        query_element = {v: k for k, v in ELEMENT_TO_FACE.items()}.get(query.home_face, "")
        element_match = 1.0 if doc_element == query_element else 0.3

        # Component 3: Archetype role constraint (if observer provides its role)
        role_fit = 0.5  # neutral default
        if archetype_role is not None:
            doc_face = ELEMENT_TO_FACE.get(doc_element, "S")
            if doc_face == archetype_role.element_affinity:
                role_fit = 0.9  # doc matches observer's element focus
            # Check if doc's structural features match role's emphasized dimensions
            if archetype_role.mode == "structural":
                # Structural roles value gate transitions
                role_fit *= 1.0 if doc.get("gate") else 0.5
            elif archetype_role.mode == "relational":
                # Relational roles value cross-chapter links
                role_fit *= min(1.0, len(doc.get("chapters", [])) / 3.0)
            elif archetype_role.mode == "recursive":
                # Recursive roles value compression quality
                role_fit *= 0.8 if doc.get("tokens") and len(doc.get("tokens", [])) > 5 else 0.4

        return token_depth * 0.4 + element_match * 0.3 + role_fit * 0.3


# ── SFCR Path Implementations ────────────────────────────────────────


class _IdfTable:
    """Inverse document frequency table built once per forward pass."""

    __slots__ = ("_idf", "_max_idf")

    def __init__(self, docs: list[dict]):
        n = max(len(docs), 1)
        doc_freq: dict[str, int] = defaultdict(int)
        for doc in docs:
            for tok in set(doc.get("tokens", [])):
                doc_freq[tok] += 1
        self._idf = {tok: math.log(n / df) for tok, df in doc_freq.items()}
        self._max_idf = max(self._idf.values()) if self._idf else 1.0

    def tfidf_score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        """TF-IDF cosine-like score between query and doc token sets."""
        if not query_tokens or not doc_tokens:
            return 0.0
        d_set = set(doc_tokens)
        score = 0.0
        norm_q = 0.0
        for tok in query_tokens:
            w = self._idf.get(tok, self._max_idf)
            norm_q += w * w
            if tok in d_set:
                score += w * w  # both query and doc have the term
        if norm_q == 0:
            return 0.0
        return score / norm_q  # [0, 1]


class SquarePath:
    """S (Earth) — Structure scoring via gate matrix transitions + shell distance."""

    @staticmethod
    def score(query: QueryState, docs: list[dict], store: FractalWeightStore,
              idf: _IdfTable = None) -> dict[str, float]:
        scores = {}
        q_gate = query.home_gate

        # Collect all gate weights to compute actual max for normalization
        gate_vals = []
        raw = {}
        for doc in docs:
            doc_id = doc.get("id", "")
            d_gate = doc.get("gate", "G00")
            gate_w = store.get_gate_weight(q_gate, d_gate)
            if gate_w == 0:
                gate_w = store.get_gate_weight(d_gate, q_gate)
            raw[doc_id] = gate_w
            if gate_w > 0:
                gate_vals.append(gate_w)

        # Normalize by actual max (not fixed 10)
        max_gw = max(gate_vals) if gate_vals else 1.0

        for doc in docs:
            doc_id = doc.get("id", "")
            # Gate transition component [0, 1]
            gate_score = raw.get(doc_id, 0.0) / max_gw if max_gw > 0 else 0.0

            # Shell proximity component [0, 1]
            doc_shell = store.doc_to_shell(doc)
            shell_dist = abs(doc_shell - query.home_shell)
            proximity = 1.0 - (shell_dist / TOTAL_SHELLS)

            # Combine: gate transition is primary, proximity is secondary
            scores[doc_id] = gate_score * 0.7 + proximity * 0.3

        return scores


class FlowerPath:
    """F (Fire) — Relation scoring via TF-IDF token matching + element affinity."""

    @staticmethod
    def score(query: QueryState, docs: list[dict], store: FractalWeightStore,
              idf: _IdfTable = None) -> dict[str, float]:
        scores = {}
        if idf is None:
            idf = _IdfTable(docs)

        for doc in docs:
            doc_id = doc.get("id", "")

            # TF-IDF token similarity (primary signal)
            tfidf = idf.tfidf_score(query.tokens, doc.get("tokens", []))

            # Element affinity from shell seed
            doc_shell = store.doc_to_shell(doc)
            seed = store.get_shell_seed(doc_shell)
            doc_element = doc.get("element", "Earth")
            if seed and seed.element_dist:
                elem_affinity = seed.element_dist.get(doc_element, 0.0)
            else:
                elem_affinity = 0.25  # uniform prior

            # Chapter co-occurrence with matched docs (relation chains)
            chain_score = 0.0
            if query.matched_docs:
                matched_chapters = set()
                for mid in query.matched_docs:
                    md = next((d for d in docs if d.get("id") == mid), None)
                    if md:
                        matched_chapters.update(md.get("chapters", []))
                doc_chapters = set(doc.get("chapters", []))
                if matched_chapters:
                    chain_score = len(doc_chapters & matched_chapters) / len(matched_chapters)

            # Weighted combination: TF-IDF dominates
            scores[doc_id] = tfidf * 0.55 + elem_affinity * 0.15 + chain_score * 0.30

        return scores


class CloudPath:
    """C (Water) — Observation scoring via neighborhood clustering + structural overlap."""

    @staticmethod
    def score(query: QueryState, docs: list[dict], store: FractalWeightStore,
              idf: _IdfTable = None) -> dict[str, float]:
        scores = {}

        # Group docs by shell for neighborhood analysis
        shell_groups: dict[int, list[dict]] = defaultdict(list)
        for doc in docs:
            shell = store.doc_to_shell(doc)
            shell_groups[shell].append(doc)

        # Build query structural signature from matched docs
        q_chapters = set()
        q_appendices = set()
        q_elements = set()
        for matched_id in query.matched_docs:
            matched = next((d for d in docs if d.get("id") == matched_id), None)
            if matched:
                q_chapters.update(matched.get("chapters", []))
                q_appendices.update(matched.get("appendices", []))
                q_elements.add(matched.get("element", ""))

        total_docs = max(len(docs), 1)

        for doc in docs:
            doc_id = doc.get("id", "")
            doc_shell = store.doc_to_shell(doc)
            neighbors = shell_groups.get(doc_shell, [])

            # Neighborhood density — use log scale to avoid saturation
            density = math.log1p(len(neighbors)) / math.log1p(total_docs)

            # Structural overlap (chapters + appendices)
            d_chapters = set(doc.get("chapters", []))
            d_appendices = set(doc.get("appendices", []))

            if q_chapters:
                ch_recall = len(d_chapters & q_chapters) / len(q_chapters)
                ch_precision = len(d_chapters & q_chapters) / max(len(d_chapters), 1)
                ch_f1 = 2 * ch_recall * ch_precision / max(ch_recall + ch_precision, 1e-10)
            else:
                ch_f1 = 0.0

            if q_appendices:
                app_recall = len(d_appendices & q_appendices) / len(q_appendices)
                app_precision = len(d_appendices & q_appendices) / max(len(d_appendices), 1)
                app_f1 = 2 * app_recall * app_precision / max(app_recall + app_precision, 1e-10)
            else:
                app_f1 = 0.0

            # Element diversity within neighborhood
            neighbor_elements = set(n.get("element", "") for n in neighbors)
            diversity = len(neighbor_elements) / 4.0  # max 4 elements

            score = density * 0.20 + ch_f1 * 0.30 + app_f1 * 0.25 + diversity * 0.25
            scores[doc_id] = score

        return scores


class FractalPath:
    """R (Air) — Compression scoring via multi-scale seed coherence."""

    @staticmethod
    def score(query: QueryState, docs: list[dict], store: FractalWeightStore,
              idf: _IdfTable = None) -> dict[str, float]:
        scores = {}

        # Pre-compute global stats for z-scoring
        all_shell_means = [s.mean for s in store.shell_seeds.values()] if store.shell_seeds else [1.0]
        global_mean = sum(all_shell_means) / len(all_shell_means)
        global_std = max(_std(all_shell_means), 0.01)

        for doc in docs:
            doc_id = doc.get("id", "")
            doc_shell = store.doc_to_shell(doc)
            archetype = ((doc_shell - 1) % 12) + 1

            # Shell-level signal
            seed = store.get_shell_seed(doc_shell)
            shell_z = 0.0
            if seed:
                # Z-score: how distinctive is this shell relative to global
                shell_z = (seed.mean - global_mean) / global_std

            # Archetype-level signal
            arch_seed = store.get_archetype_seed(archetype)
            arch_coherence = 0.5
            if arch_seed and arch_seed.wreath_means:
                # How consistent are the 3 wreaths? Lower variance = higher coherence
                wreath_vals = list(arch_seed.wreath_means.values())
                if len(wreath_vals) > 1:
                    wreath_std = _std(wreath_vals)
                    arch_coherence = max(0.0, 1.0 - wreath_std / max(abs(arch_seed.mean), 0.01))

            # Compression quality: reconstruction error
            decomp = store.decompress_from_seed(doc_shell)
            compress_quality = 0.5
            if decomp and seed:
                error = decomp.get("reconstruction_error", 0.0)
                compress_quality = max(0.0, 1.0 - error / max(abs(seed.mean), 0.01))

            # Query alignment via seed element distribution
            query_face = query.home_face
            query_element = FACE_TO_ELEMENT.get(query_face, "Earth")
            elem_alignment = 0.25
            if seed and seed.element_dist:
                elem_alignment = seed.element_dist.get(doc.get("element", "Earth"), 0.25)

            # Combine with z-score driving discrimination
            # Sigmoid of z-score to [0,1] — docs with distinctive shells score higher
            z_signal = 1.0 / (1.0 + math.exp(-shell_z))

            score = (z_signal * 0.35
                     + arch_coherence * 0.20
                     + compress_quality * 0.20
                     + elem_alignment * 0.25)

            scores[doc_id] = max(0.0, min(score, 1.0))

        return scores


def _std(values: list[float]) -> float:
    """Standard deviation helper."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


# ── Crystal Neural Engine ────────────────────────────────────────────


class CrystalNeuralEngine:
    """Forward-pass engine with 4 SFCR processing paths."""

    PATHS = {
        "S": SquarePath,
        "F": FlowerPath,
        "C": CloudPath,
        "R": FractalPath,
    }

    RESONANCE_THRESHOLD = 0.4

    def __init__(self, store: FractalWeightStore = None):
        self.store = store or get_store()

    def _tokenize_query(self, raw_query: str) -> list[str]:
        """Simple token extraction from query text."""
        import re
        text = raw_query.lower()
        # Remove punctuation, split
        tokens = re.findall(r'[a-z][a-z0-9_]+', text)
        # Remove common stopwords
        stops = {"the", "and", "for", "with", "this", "that", "from", "into",
                 "are", "was", "were", "been", "being", "have", "has", "had",
                 "not", "but", "what", "how", "when", "where", "who", "which"}
        return [t for t in tokens if t not in stops and len(t) > 2]

    def _build_query_state(self, raw_query: str) -> QueryState:
        """Convert raw text query into a QueryState."""
        tokens = self._tokenize_query(raw_query)
        docs = self.store.doc_registry

        if not docs:
            return QueryState(raw_query=raw_query, tokens=tokens)

        # Find best-matching docs by token overlap
        doc_scores = []
        for doc in docs:
            d_tokens = set(doc.get("tokens", []))
            overlap = len(set(tokens) & d_tokens)
            if overlap > 0:
                doc_scores.append((doc, overlap))

        doc_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = doc_scores[:5]

        if top_docs:
            best_doc = top_docs[0][0]
            home_shell = self.store.doc_to_shell(best_doc)
            home_face = ELEMENT_TO_FACE.get(best_doc.get("element", "Earth"), "S")
            home_gate = best_doc.get("gate", "G00")
            matched_ids = [d[0]["id"] for d in top_docs]
        else:
            home_shell = 1
            home_face = "S"
            home_gate = "G00"
            matched_ids = []

        return QueryState(
            raw_query=raw_query,
            tokens=tokens,
            home_shell=home_shell,
            home_face=home_face,
            home_gate=home_gate,
            matched_docs=matched_ids,
        )

    def forward(self, query: str | QueryState, max_results: int = 10) -> ForwardResult:
        """Full forward pass: query → 4 SFCR paths → bridge merge → ranked results."""
        t0 = time.time()

        if isinstance(query, str):
            qs = self._build_query_state(query)
        else:
            qs = query

        docs = self.store.doc_registry
        if not docs:
            return ForwardResult(query=qs, elapsed_ms=0)

        # Build IDF table once for all paths
        idf = _IdfTable(docs)

        # 1. Run 4 SFCR paths
        sfcr_scores = {}
        for face, path_cls in self.PATHS.items():
            sfcr_scores[face] = path_cls.score(qs, docs, self.store, idf)

        # 2. Bridge merge — GEOMETRIC mean + multiplicative bridge modulation
        #    This preserves discrimination: if any path gives low score, merged stays low
        doc_lookup = {d["id"]: d for d in docs}
        merged = {}
        cross_pairs = []

        # Path importance weights (learnable — stored in crystal weights)
        path_weights = self.store.path_weights
        geo_blend = self.store.geo_arith_blend
        bridge_mod = self.store.bridge_modulation

        for doc_id in set().union(*[s.keys() for s in sfcr_scores.values()]):
            path_contribs = {}
            for face in "SFCR":
                path_contribs[face] = sfcr_scores.get(face, {}).get(doc_id, 0.0)

            # Weighted power mean (p=-1 = harmonic-ish, preserves low scores)
            # For docs with all-zero scores, result is 0
            weighted_sum = 0.0
            weight_total = 0.0
            log_sum = 0.0
            has_nonzero = False
            for face in "SFCR":
                s = path_contribs[face]
                w = path_weights[face]
                weighted_sum += w * s
                weight_total += w
                if s > 1e-8:
                    log_sum += w * math.log(s + 1e-10)
                    has_nonzero = True

            # Arithmetic mean as base
            arith = weighted_sum / max(weight_total, 1e-10)

            # Geometric mean (preserves discrimination — low path scores pull it down)
            if has_nonzero:
                geo = math.exp(log_sum / max(weight_total, 1e-10))
            else:
                geo = 0.0

            # Blend: geometric prevents saturation, arithmetic prevents collapse
            base = geo_blend * geo + (1.0 - geo_blend) * arith

            # Bridge modulation: MULTIPLICATIVE, not additive
            # Cross-element coherence boosts score slightly (max ~20% boost)
            bridge_coherence = 0.0
            doc = doc_lookup.get(doc_id, {})

            for face_a in "SFCR":
                for face_b in "SFCR":
                    if face_a >= face_b:
                        continue
                    key = _bridge_key(face_a, face_b)
                    bw = BRIDGE_WEIGHTS.get(key, 0.382)
                    s_a = path_contribs.get(face_a, 0.0)
                    s_b = path_contribs.get(face_b, 0.0)
                    cross = bw * min(s_a, s_b)  # min preserves discrimination
                    bridge_coherence += cross
                    if cross > 0.01:
                        cross_pairs.append(f"{face_a}{face_b}:{doc_id}")

            # Normalize bridge coherence to [0, 1] (max possible = sum of all bridge weights)
            max_bridge = sum(BRIDGE_WEIGHTS.values())  # ~3.236
            bridge_factor = 1.0 + bridge_mod * (bridge_coherence / max(max_bridge, 1.0))

            merged[doc_id] = base * bridge_factor
            # No min(1.0) clamp — let scores spread naturally

        # 3. Compute resonance, desire, action for top candidates
        ranked = []
        sorted_ids = sorted(merged, key=lambda x: merged[x], reverse=True)

        for doc_id in sorted_ids[:max_results * 2]:
            doc = doc_lookup.get(doc_id)
            if not doc:
                continue

            resonance = ResonanceComputer.compute(qs, doc, self.store)
            desire = DesireComputer.compute(qs, doc, self.store)
            kinetic = 1.0 - merged.get(doc_id, 0.0)  # K(X) = distance from perfect score
            action = kinetic - desire  # minimize action

            path_contribs = {}
            for face in "SFCR":
                path_contribs[face] = sfcr_scores.get(face, {}).get(doc_id, 0.0)

            ranked.append(RankedCandidate(
                doc_id=doc_id,
                doc_name=doc.get("display_name", doc.get("name", doc_id))[:100],
                element=doc.get("element", "unknown"),
                gate=doc.get("gate", "G00"),
                shell=self.store.doc_to_shell(doc),
                merged_score=merged.get(doc_id, 0.0),
                action=action,
                resonance=resonance,
                desire=desire,
                path_contributions=path_contribs,
            ))

        # Sort by action (minimize) — lower action = better
        ranked.sort(key=lambda c: c.action)
        ranked = ranked[:max_results]

        # 4. Compute overall resonance and commit
        overall_resonance = sum(c.resonance for c in ranked) / max(len(ranked), 1)

        commit = CommitWitness(
            resonance_gate=overall_resonance >= self.RESONANCE_THRESHOLD,
            boundary_gate=all(1 <= c.shell <= TOTAL_SHELLS for c in ranked),
            crossview_gate=len(set(c.element for c in ranked)) >= 2,  # at least 2 elements
            scale_gate=all(c.resonance > 0.1 for c in ranked),
        )
        commit.committed = all([
            commit.resonance_gate,
            commit.boundary_gate,
            commit.crossview_gate,
            commit.scale_gate,
        ])
        commit.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        elapsed = (time.time() - t0) * 1000

        return ForwardResult(
            query=qs,
            candidates=ranked,
            resonance=overall_resonance,
            committed=commit.committed,
            commit_witness=commit,
            sfcr_scores={f: dict(list(s.items())[:5]) for f, s in sfcr_scores.items()},
            elapsed_ms=elapsed,
            cross_element_pairs_used=cross_pairs[:20],
        )


    def forward_for_observer(
        self,
        query: str | QueryState,
        observer: "ObserverAgent",
        max_results: int = 10,
    ) -> "ObserverResult":
        """Run a forward pass biased by an observer agent's element/archetype/liminal lens.

        The observer's element gets its path weight multiplied by element_bias (default 2x).
        The observer's archetype role modifies constraint_satisfaction scoring.
        The observer's liminal coordinate modifies boundary_fit scoring.

        Returns an ObserverResult (not a ForwardResult) with:
          - Element-biased rankings
          - 12D observation scores weighted by archetype role
          - Path contribution breakdown showing element balance
        """
        from .observer_agent import ObserverResult
        from .archetype_roles import get_role
        from .liminal_mapper import get_coordinate

        t0 = time.time()

        if isinstance(query, str):
            qs = self._build_query_state(query)
        else:
            qs = query

        docs = self.store.doc_registry
        if not docs:
            return ObserverResult(agent=observer, elapsed_ms=0)

        # Get observer's role and liminal coordinate
        role = get_role(observer.archetype_idx)
        liminal = get_coordinate(observer.liminal_coord)

        # Build IDF table
        idf = _IdfTable(docs)

        # 1. Run 4 SFCR paths with element bias
        sfcr_scores = {}
        for face, path_cls in self.PATHS.items():
            sfcr_scores[face] = path_cls.score(qs, docs, self.store, idf)

        # 2. Biased merge — observer's element gets upweighted
        base_weights = dict(self.store.path_weights)
        biased_weights = dict(base_weights)
        obs_element = observer.element
        if obs_element in biased_weights:
            biased_weights[obs_element] *= observer.element_bias
        # Renormalize
        total_w = sum(biased_weights.values())
        if total_w > 0:
            biased_weights = {k: v / total_w for k, v in biased_weights.items()}

        geo_blend = self.store.geo_arith_blend
        bridge_mod = self.store.bridge_modulation
        doc_lookup = {d["id"]: d for d in docs}
        merged = {}

        for doc_id in set().union(*[s.keys() for s in sfcr_scores.values()]):
            path_contribs = {f: sfcr_scores.get(f, {}).get(doc_id, 0.0) for f in "SFCR"}

            weighted_sum = 0.0
            weight_total = 0.0
            log_sum = 0.0
            has_nonzero = False
            for face in "SFCR":
                s = path_contribs[face]
                w = biased_weights.get(face, 0.25)
                weighted_sum += w * s
                weight_total += w
                if s > 1e-8:
                    log_sum += w * math.log(s + 1e-10)
                    has_nonzero = True

            arith = weighted_sum / max(weight_total, 1e-10)
            geo = math.exp(log_sum / max(weight_total, 1e-10)) if has_nonzero else 0.0
            base = geo_blend * geo + (1.0 - geo_blend) * arith

            # Bridge modulation
            bridge_coherence = 0.0
            from .neural_engine import BRIDGE_WEIGHTS as BW
            for fa in "SFCR":
                for fb in "SFCR":
                    if fa >= fb:
                        continue
                    key = _bridge_key(fa, fb)
                    bw = BW.get(key, 0.382)
                    bridge_coherence += bw * min(path_contribs.get(fa, 0), path_contribs.get(fb, 0))

            max_bridge = sum(BW.values())
            bridge_factor = 1.0 + bridge_mod * (bridge_coherence / max(max_bridge, 1.0))
            merged[doc_id] = base * bridge_factor

        # 3. Rank by action minimization with role-aware resonance/desire
        ranked_ids = sorted(merged, key=lambda x: merged[x], reverse=True)[:max_results]
        ranked_scores = [merged[did] for did in ranked_ids]

        # Compute mean path contributions for the observer
        mean_contribs = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
        for did in ranked_ids:
            for face in "SFCR":
                mean_contribs[face] += sfcr_scores.get(face, {}).get(did, 0.0)
        n = max(len(ranked_ids), 1)
        mean_contribs = {k: v / n for k, v in mean_contribs.items()}

        # Compute resonance/desire for top result
        top_resonance = 0.0
        top_desire = 0.0
        if ranked_ids:
            top_doc = doc_lookup.get(ranked_ids[0])
            if top_doc:
                top_resonance = ResonanceComputer.compute(qs, top_doc, self.store)
                top_desire = DesireComputer.compute(qs, top_doc, self.store)

        # 4. Score discrimination
        if ranked_scores:
            disc_mean = sum(ranked_scores) / len(ranked_scores)
            discrimination = math.sqrt(
                sum((s - disc_mean) ** 2 for s in ranked_scores) / max(len(ranked_scores), 1)
            )
        else:
            discrimination = 0.0

        # 5. Build 12D observation using archetype role weights
        observation_12d = {}
        dim_names = [
            "x1_structure", "x2_semantics", "x3_coordination", "x4_recursion",
            "x5_contradiction", "x6_emergence", "x7_legibility", "x8_routing",
            "x9_grounding", "x10_compression", "x11_interop", "x12_potential",
        ]
        for dim in dim_names:
            base_score = 0.5  # neutral
            role_weight = role.dim_weights.get(dim, 1.0)
            # Map dimensions to observable quantities
            if "structure" in dim:
                base_score = mean_contribs.get("S", 0.0)
            elif "semantics" in dim:
                base_score = mean_contribs.get("F", 0.0)
            elif "coordination" in dim:
                base_score = (mean_contribs.get("S", 0) + mean_contribs.get("C", 0)) / 2
            elif "recursion" in dim:
                base_score = mean_contribs.get("R", 0.0)
            elif "contradiction" in dim:
                # High variance in path contributions = contradiction
                vals = list(mean_contribs.values())
                base_score = _std(vals) if vals else 0.0
            elif "emergence" in dim:
                base_score = mean_contribs.get("C", 0.0)
            elif "legibility" in dim:
                base_score = discrimination
            elif "routing" in dim:
                base_score = top_resonance
            elif "grounding" in dim:
                base_score = top_desire
            elif "compression" in dim:
                base_score = mean_contribs.get("R", 0.0)
            elif "interop" in dim:
                # Cross-element coherence
                base_score = min(mean_contribs.values()) if mean_contribs else 0.0
            elif "potential" in dim:
                base_score = max(ranked_scores) - min(ranked_scores) if ranked_scores else 0.0

            observation_12d[dim] = base_score * role_weight

        elapsed = (time.time() - t0) * 1000

        return ObserverResult(
            agent=observer,
            ranked_doc_ids=ranked_ids,
            ranked_scores=ranked_scores,
            path_contributions=mean_contribs,
            observation_12d=observation_12d,
            resonance=top_resonance,
            desire=top_desire,
            discrimination=discrimination,
            elapsed_ms=elapsed,
            committed=top_resonance >= self.RESONANCE_THRESHOLD,
        )


# ── Singleton engine ─────────────────────────────────────────────────

_ENGINE: Optional[CrystalNeuralEngine] = None


def get_engine() -> CrystalNeuralEngine:
    """Get or create the singleton CrystalNeuralEngine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = CrystalNeuralEngine()
    return _ENGINE


# ── MCP tool entry point ─────────────────────────────────────────────


def neural_forward_pass(
    query: str = "seed kernel",
    max_results: int = 10,
    verbose: bool = False,
) -> str:
    """Run a forward pass through the crystal neural engine.

    Routes the query through 4 SFCR processing paths (Square/Flower/Cloud/Fractal),
    merges via brain bridge weights, and ranks by action minimization.

    Args:
        query: Text query to process through the neural network
        max_results: Maximum number of results to return (1-20)
        verbose: Include detailed SFCR path scores and commit witness
    """
    engine = get_engine()
    max_results = max(1, min(max_results, 20))

    result = engine.forward(query, max_results=max_results)
    return _format_forward_result(result, verbose)


def _format_forward_result(result: ForwardResult, verbose: bool = False) -> str:
    qs = result.query
    lines = [
        "## Crystal Neural Forward Pass\n",
        f"**Query**: `{qs.raw_query}`",
        f"**Tokens**: {', '.join(qs.tokens[:15])}",
        f"**Home**: S{qs.home_shell} / {qs.home_face} / {qs.home_gate}",
        f"**Matched Docs**: {len(qs.matched_docs)}",
        f"**Overall Resonance**: {result.resonance:.4f}",
        f"**Committed**: {'YES' if result.committed else 'NO'}",
        f"**Elapsed**: {result.elapsed_ms:.1f}ms\n",
    ]

    # Ranked results
    lines.append("### Results (ranked by action minimization)\n")
    lines.append("| # | Doc | Element | Gate | Shell | Score | Action | Resonance | Desire |")
    lines.append("|---|-----|---------|------|-------|-------|--------|-----------|--------|")

    for i, c in enumerate(result.candidates, 1):
        name = c.doc_name[:50]
        lines.append(
            f"| {i} | {name} | {c.element} | {c.gate} | S{c.shell} | "
            f"{c.merged_score:.3f} | {c.action:.3f} | {c.resonance:.3f} | {c.desire:.3f} |"
        )

    if verbose and result.commit_witness:
        cw = result.commit_witness
        lines.extend([
            "\n### Commit Witness\n",
            f"- **Resonance Gate** (R ≥ τ): {'PASS' if cw.resonance_gate else 'FAIL'}",
            f"- **Boundary Gate**: {'PASS' if cw.boundary_gate else 'FAIL'}",
            f"- **Crossview Gate** (≥2 elements): {'PASS' if cw.crossview_gate else 'FAIL'}",
            f"- **Scale Gate**: {'PASS' if cw.scale_gate else 'FAIL'}",
            f"- **Committed**: {'YES' if cw.committed else 'NO'}",
        ])

    if verbose and result.candidates:
        lines.append("\n### SFCR Path Contributions (top result)\n")
        top = result.candidates[0]
        for face in "SFCR":
            score = top.path_contributions.get(face, 0.0)
            name = LENS_CODES.get(face, face)
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {face} ({name:7s}): {bar} {score:.3f}")

    if verbose and result.cross_element_pairs_used:
        lines.append(f"\n### Cross-Element Bridges Used: {len(result.cross_element_pairs_used)}")
        for pair in result.cross_element_pairs_used[:5]:
            lines.append(f"  - {pair}")

    return "\n".join(lines)
