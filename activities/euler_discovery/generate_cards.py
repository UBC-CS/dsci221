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
    """Connected graph where every vertex has even degree — varied and dense."""
    r = random.Random(seed)
    for _ in range(2000):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        # Hamiltonian cycle backbone (ensures connectivity)
        perm = list(range(n))
        r.shuffle(perm)
        for i in range(n):
            G.add_edge(perm[i], perm[(i + 1) % n])
        # XOR with 2–4 random cycles of length 3–5.
        # XOR-ing a cycle toggles each of its edges (add if absent, remove if present)
        # and preserves all-even degrees, so the graph stays Eulerian-eligible.
        for _ in range(r.randint(2, 4)):
            k = r.randint(3, min(5, n))
            nodes = r.sample(range(n), k)
            for i in range(k):
                u, v = nodes[i], nodes[(i + 1) % k]
                if G.has_edge(u, v):
                    G.remove_edge(u, v)
                else:
                    G.add_edge(u, v)
        # Require density beyond a bare cycle and full Eulerian conditions
        if nx.is_eulerian(G) and G.number_of_edges() >= n + 3:
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


def gen_neither(n, seed, pairs=2):
    """Connected graph with exactly 2*pairs odd-degree vertices (pairs ≥ 2).

    Add `pairs` vertex-disjoint non-edges to a circuit base.  Each added edge
    flips two previously-even vertices to odd, so the result has exactly
    2*pairs odd-degree vertices.  Use pairs=n//2 on even n for all-odd.
    """
    r = random.Random(seed)
    for _ in range(2000):
        G = gen_circuit(n, r.randint(0, 999_999))
        if G is None:
            continue
        non_edges = [(u, v) for u in G for v in G if u < v and not G.has_edge(u, v)]
        r.shuffle(non_edges)
        G2, added, used = G.copy(), 0, set()
        for u, v in non_edges:
            if u not in used and v not in used:
                G2.add_edge(u, v)
                used |= {u, v}
                added += 1
            if added == pairs:
                break
        actual_odd = sum(1 for v in G2 if G2.degree(v) % 2 == 1)
        if actual_odd == 2 * pairs and nx.is_connected(G2):
            return G2
    return None


# ── Generate all 30 graphs ────────────────────────────────────────────────────
print("Generating graphs…")

# Distribution:
#   10 × Euler circuit  (0 odd-degree vertices)
#   10 × Euler path     (exactly 2 odd-degree vertices)
#    4 × Neither, 4 odd (pairs=2)
#    4 × Neither, 6 odd (pairs=3, n≥7 so not all-odd)
#    2 × Neither, all odd (pairs=n//2, n=6 → 6 odd; n=8 → 8 odd)
specs = (
    [("circuit", gen_circuit,                                 n, 1000+i)
        for i, n in enumerate([6,7,7,8,6,7,8,6,7,8])] +
    [("path",    gen_path_only,                               n, 2000+i)
        for i, n in enumerate([7,6,8,7,6,8,7,6,8,7])] +
    [("4odd",    lambda n, s: gen_neither(n, s, pairs=2),     n, 3000+i)
        for i, n in enumerate([7,6,8,7])] +
    [("6odd",    lambda n, s: gen_neither(n, s, pairs=3),     n, 4000+i)
        for i, n in enumerate([7,8,7,8])] +
    [("allOdd",  lambda n, s: gen_neither(n, s, pairs=n//2),  n, 5000+i)
        for i, n in enumerate([6,8])]
)

EXPECTED = {
    "circuit": "Euler circuit",
    "path":    "Euler path only",
    "4odd":    "Neither",
    "6odd":    "Neither",
    "allOdd":  "Neither",
}

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

def draw_card(ax, G, label):
    """Render an adjacency-list table: vertex | neighbors."""
    ax.axis("off")
    ax.set_title(label, fontsize=15, fontweight="bold", pad=10)

    verts = sorted(G.nodes())
    table_data = [[v, ", ".join(sorted(G.neighbors(v)))] for v in verts]

    tbl = ax.table(
        cellText=table_data,
        colLabels=["Vertex", "Neighbors"],
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(13)
    tbl.scale(0.9, 2.2)

    # Style header row
    for col in range(2):
        tbl[0, col].set_facecolor("#dde8f0")
        tbl[0, col].set_text_props(fontweight="bold")
    # Widen the Neighbors column relative to Vertex column
    tbl.auto_set_column_width([0, 1])


# ── Render PDF ────────────────────────────────────────────────────────────────
PDF = "euler_cards.pdf"
print(f"\nRendering {PDF}…")

with PdfPages(PDF) as pdf:
    for i in range(0, 30, 2):
        fig = plt.figure(figsize=(11, 8.5))
        # 2 columns (cards), 2 rows: table on top, drawing box on bottom
        gs = fig.add_gridspec(2, 2,
                              height_ratios=[1, 1.6],
                              left=0.04, right=0.96,
                              top=0.93, bottom=0.04,
                              wspace=0.18, hspace=0.25)

        for slot in range(2):
            ci = i + slot
            ax_table = fig.add_subplot(gs[0, slot])
            ax_draw  = fig.add_subplot(gs[1, slot])

            if ci >= 30:
                ax_table.axis("off")
                ax_draw.axis("off")
                continue

            G, label, _ = cards[ci]
            draw_card(ax_table, G, label)

            # Blank drawing area with a light border
            ax_draw.set_xlim(0, 1)
            ax_draw.set_ylim(0, 1)
            ax_draw.set_xticks([])
            ax_draw.set_yticks([])
            for spine in ax_draw.spines.values():
                spine.set_edgecolor("#aaa")
                spine.set_linewidth(1)

        # Dashed cut line between cards
        fig.add_artist(plt.Line2D([0.5, 0.5], [0.02, 0.98],
                                  transform=fig.transFigure,
                                  color="#bbb", linewidth=1, linestyle="--"))

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

print(f"Done — {PDF}  (15 pages · 2 cards per page · cut along dashed line)")
