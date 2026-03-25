#!/usr/bin/env python3
"""
generate_cards.py — Generate 30 graph cards for the Euler path discovery activity.

30 cards, shuffled:
  10 × Euler circuit    (all vertices have even degree)
  10 × Euler path only  (exactly 2 odd-degree vertices)
  10 × Neither          (4+ odd-degree vertices)

Output:
  euler_cards.pdf      — 15 pages, 2 cards per page; print and cut in half
  euler_answer_key.txt — instructor key

Usage:
  pip install networkx matplotlib
  python generate_cards.py
"""

import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_pdf import PdfPages

# ── Reproducibility ───────────────────────────────────────────────────────────
SEED = 221
rng  = random.Random(SEED)

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ── Utilities ─────────────────────────────────────────────────────────────────
def relabel(G):
    return nx.relabel_nodes(G, {n: LETTERS[i] for i, n in enumerate(sorted(G.nodes()))})

def euler_type(G):
    if not nx.is_connected(G):     return "disconnected"
    if nx.is_eulerian(G):          return "Euler circuit"
    if nx.has_eulerian_path(G):    return "Euler path only"
    return "Neither"

# ── Graph generators ──────────────────────────────────────────────────────────

def gen_circuit(n, seed):
    """Connected graph where every vertex has even degree."""
    r = random.Random(seed)
    for _ in range(2000):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        # Random Hamiltonian cycle → all degree 2 (even)
        perm = list(range(n))
        r.shuffle(perm)
        for i in range(n):
            G.add_edge(perm[i], perm[(i + 1) % n])
        # Optionally add extra edge-disjoint triangles (each adds 2 to three degrees → stays even)
        for _ in range(r.randint(1, 3)):
            a, b, c = r.sample(range(n), 3)
            if not G.has_edge(a, b) and not G.has_edge(b, c) and not G.has_edge(a, c):
                G.add_edges_from([(a, b), (b, c), (a, c)])
        if nx.is_eulerian(G):   # is_eulerian checks connected + all-even
            return relabel(G)
    return None


def gen_path_only(n, seed):
    """Connected graph with exactly 2 odd-degree vertices."""
    r = random.Random(seed)
    for _ in range(2000):
        G = gen_circuit(n, r.randint(0, 999_999))
        if G is None:
            continue
        # Add one non-existing edge → its two endpoints become odd
        non_edges = [(u, v) for u in G for v in G if u < v and not G.has_edge(u, v)]
        if not non_edges:
            continue
        G.add_edge(*r.choice(non_edges))
        if euler_type(G) == "Euler path only":
            return G
    return None


def gen_neither(n, seed):
    """Connected graph with ≥ 4 odd-degree vertices."""
    r = random.Random(seed)
    for _ in range(2000):
        G = gen_circuit(n, r.randint(0, 999_999))
        if G is None:
            continue
        # Add two vertex-disjoint non-edges → 4 distinct vertices become odd
        non_edges = [(u, v) for u in G for v in G if u < v and not G.has_edge(u, v)]
        r.shuffle(non_edges)
        G2, added, used = G.copy(), 0, set()
        for u, v in non_edges:
            if u not in used and v not in used:
                G2.add_edge(u, v)
                used |= {u, v}
                added += 1
            if added == 2:
                break
        if euler_type(G2) == "Neither":
            return G2
    return None


# ── Generate all 30 graphs ────────────────────────────────────────────────────
print("Generating graphs…")

specs = (
    [("circuit", gen_circuit,   n, 1000+i) for i,n in enumerate([6,7,7,8,6,7,8,6,7,8])] +
    [("path",    gen_path_only, n, 2000+i) for i,n in enumerate([7,6,8,7,6,8,7,6,8,7])] +
    [("neither", gen_neither,   n, 3000+i) for i,n in enumerate([7,6,8,7,6,8,7,6,8,7])]
)

EXPECTED = {"circuit": "Euler circuit", "path": "Euler path only", "neither": "Neither"}

pool = []
for kind, fn, n, seed in specs:
    G = fn(n, seed)
    if G is None:
        raise RuntimeError(f"Failed to generate {kind} n={n} seed={seed}")
    actual = euler_type(G)
    if actual != EXPECTED[kind]:
        raise RuntimeError(f"Wrong type for {kind}: got {actual!r}")
    pool.append((G, kind))
    odd = sorted(v for v in G if G.degree(v) % 2 == 1)
    print(f"  {kind:12s}  n={G.number_of_nodes()}  m={G.number_of_edges():2d}"
          f"  odd={odd or '(none)'}")

rng.shuffle(pool)
cards = [(G, f"Card {i+1:02d}", kind) for i, (G, kind) in enumerate(pool)]

# ── Answer key ────────────────────────────────────────────────────────────────
KEY = "euler_answer_key.txt"
print(f"\n{'─'*55}")
print(f"{'Card':<10}  {'Type':<22}  Odd-degree vertices")
print(f"{'─'*55}")
with open(KEY, "w") as f:
    f.write("EULER PATH DISCOVERY — ANSWER KEY\n")
    f.write("=" * 55 + "\n\n")
    f.write(f"{'Card':<10}  {'Type':<22}  Odd-degree vertices\n")
    f.write("-" * 55 + "\n")
    for G, label, kind in cards:
        odd = sorted(v for v in G if G.degree(v) % 2 == 1)
        t   = euler_type(G)
        row = f"{label:<10}  {t:<22}  {odd or '(none)'}"
        print(row)
        f.write(row + "\n")
print(f"\nAnswer key → {KEY}")

# ── Drawing ───────────────────────────────────────────────────────────────────
EDGE_KW  = dict(edge_color="#333", width=2.5, alpha=0.9)
NODE_KW  = dict(node_color="white", node_size=900, edgecolors="#222", linewidths=2.5)
LABEL_KW = dict(font_size=13, font_weight="bold", font_color="#111")


def draw_graph(ax, G, label, seed):
    pos = nx.spring_layout(G, seed=seed, k=1.8)
    nx.draw_networkx_edges(G, pos, ax=ax, **EDGE_KW)
    nx.draw_networkx_nodes(G, pos, ax=ax, **NODE_KW)
    nx.draw_networkx_labels(G, pos, ax=ax, **LABEL_KW)
    ax.set_title(label, fontsize=15, fontweight="bold", pad=10)
    ax.axis("off")


def annotate(ax, G):
    """Degree table and checkboxes below the graph axes."""
    verts   = sorted(G.nodes())
    deg_str = "   ".join(f"{v}: ___" for v in verts)
    kw = dict(ha="center", va="top", transform=ax.transAxes, clip_on=False)

    ax.text(0.5, -0.05,
            "Try to trace every edge exactly once without lifting your pencil.",
            fontsize=9, color="#444", style="italic", **kw)
    ax.text(0.5, -0.14,
            "Degree of each vertex:",
            fontsize=9, color="#555", style="italic", **kw)
    ax.text(0.5, -0.23, deg_str,
            fontsize=10, family="monospace", **kw)
    ax.text(0.5, -0.34,
            "# of odd-degree vertices: _______",
            fontsize=10, **kw)
    ax.text(0.5, -0.45,
            "[ ] Euler circuit     [ ] Euler path (not circuit)     [ ] Neither",
            fontsize=9, **kw)


# ── Render PDF ────────────────────────────────────────────────────────────────
PDF = "euler_cards.pdf"
print(f"\nRendering {PDF}…")

with PdfPages(PDF) as pdf:
    for i in range(0, 30, 2):
        fig, axes = plt.subplots(1, 2, figsize=(11, 8.5))
        fig.subplots_adjust(left=0.04, right=0.96, top=0.93, bottom=0.42, wspace=0.18)

        for slot, ax in enumerate(axes):
            ci = i + slot
            if ci >= 30:
                ax.axis("off")
                continue
            G, label, _ = cards[ci]
            draw_graph(ax, G, label, seed=ci * 7 + 13)
            annotate(ax, G)

        # Dashed cut line between cards
        fig.add_artist(plt.Line2D([0.5, 0.5], [0.02, 0.98],
                                  transform=fig.transFigure,
                                  color="#bbb", linewidth=1, linestyle="--"))

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

print(f"Done — {PDF}  (15 pages · 2 cards per page · cut along dashed line)")
