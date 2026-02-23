#!/usr/bin/env python3
"""
Jotto Decision Tree Simulator

Builds COMPLETE decision trees that work for ANY secret word.
Each node: "Guess this word"
Each edge: Jotto score (0, 1, 2, or 3)
Each leaf: "The secret must be this word"

Compares BEST (minimax depth) vs WORST (maximize depth) strategies.
"""

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
import html

# Word set where different heuristics produce DIFFERENT decision trees!
# - Greedy Minimax: first guess MOB, depth 8
# - Information Gain: first guess NIP, depth 7
# - Min Average: first guess NAP, depth 6 (matches optimal!)
# No anagram pairs in this set.
WORDS = [
    "fox", "gel", "ink", "jog",
    "mob", "nap", "nip", "nor",
    "nut", "oat", "oil", "pug",
    "soy", "dew", "woo", "yak"
]

def jotto_score(guess: str, secret: str) -> int:
    """Count letters in common (Jotto scoring)."""
    return len(set(guess) & set(secret))

def partition_by_score(guess: str, candidates: list[str]) -> dict[int, list[str]]:
    """Partition candidates by their Jotto score against guess."""
    groups = defaultdict(list)
    for word in candidates:
        score = jotto_score(guess, word)
        groups[score].append(word)
    return dict(groups)

@dataclass
class TreeNode:
    guess: str
    children: dict[int, 'TreeNode'] = field(default_factory=dict)  # score -> subtree
    is_leaf: bool = False

    def depth(self) -> int:
        if self.is_leaf or not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children.values())

    def total_nodes(self) -> int:
        if self.is_leaf or not self.children:
            return 1
        return 1 + sum(child.total_nodes() for child in self.children.values())

    def num_leaves(self) -> int:
        if self.is_leaf or not self.children:
            return 1
        return sum(child.num_leaves() for child in self.children.values())

    def sum_leaf_depths(self, current_depth: int = 1) -> int:
        """Sum of depths of all leaves (for computing average)."""
        if self.is_leaf or not self.children:
            return current_depth
        return sum(child.sum_leaf_depths(current_depth + 1) for child in self.children.values())

    def average_depth(self) -> float:
        """Average depth to reach a leaf (expected guesses if uniform distribution)."""
        return self.sum_leaf_depths() / self.num_leaves()


def build_tree_minimax_greedy(candidates: list[str]) -> TreeNode:
    """
    Build COMPLETE tree using BEST strategy: minimize worst-case depth.
    This tree can identify ANY word in `candidates`.
    """
    if len(candidates) == 0:
        return TreeNode(guess="???", is_leaf=True)
    if len(candidates) == 1:
        return TreeNode(guess=candidates[0], is_leaf=True)

    # Find guess that minimizes the maximum partition size
    best_guess = None
    best_max_partition = float('inf')
    best_partitions = None

    for guess in candidates:
        partitions = partition_by_score(guess, candidates)
        # Score 3 means we found it (guess == secret), so that partition has size 1
        max_size = 0
        for score, words in partitions.items():
            if score == 3:
                # This is the "found it" case - only contains `guess` itself
                continue
            max_size = max(max_size, len(words))

        if max_size < best_max_partition:
            best_max_partition = max_size
            best_guess = guess
            best_partitions = partitions

    if best_guess is None:
        best_guess = candidates[0]
        best_partitions = partition_by_score(best_guess, candidates)

    # Build subtrees for each possible score
    children = {}
    for score in range(4):  # 0, 1, 2, 3
        if score in best_partitions:
            remaining = best_partitions[score]
            if score == 3:
                # Score 3 means guess == secret, so it's a leaf
                children[score] = TreeNode(guess=best_guess, is_leaf=True)
            else:
                # Remove the guess from remaining if present (we guessed it, wasn't the answer)
                remaining = [w for w in remaining if w != best_guess]
                if remaining:
                    children[score] = build_tree_minimax_greedy(remaining)

    return TreeNode(guess=best_guess, children=children)


def build_tree_true_minimax(candidates: list[str], memo: dict = None) -> TreeNode:
    """
    Build tree using TRUE minimax: exhaustively search all possible first guesses
    and recursively find the one that minimizes worst-case depth.
    """
    if memo is None:
        memo = {}

    key = tuple(sorted(candidates))
    if key in memo:
        return memo[key]

    if len(candidates) == 0:
        return TreeNode(guess="???", is_leaf=True)
    if len(candidates) == 1:
        return TreeNode(guess=candidates[0], is_leaf=True)

    best_tree = None
    best_depth = float('inf')

    for guess in candidates:
        partitions = partition_by_score(guess, candidates)

        # Build subtrees for each partition
        children = {}
        max_child_depth = 0

        for score in range(4):
            if score in partitions:
                remaining = partitions[score]
                if score == 3:
                    children[score] = TreeNode(guess=guess, is_leaf=True)
                else:
                    remaining = [w for w in remaining if w != guess]
                    if remaining:
                        child_tree = build_tree_true_minimax(remaining, memo)
                        children[score] = child_tree
                        max_child_depth = max(max_child_depth, child_tree.depth())

        tree_depth = 1 + max_child_depth

        if tree_depth < best_depth:
            best_depth = tree_depth
            best_tree = TreeNode(guess=guess, children=children)

    memo[key] = best_tree
    return best_tree


def build_tree_min_average(candidates: list[str], memo: dict = None) -> TreeNode:
    """
    Build tree that minimizes AVERAGE depth (expected guesses).
    Greedy: at each step, pick guess that minimizes weighted average of partition sizes.
    """
    if memo is None:
        memo = {}

    key = tuple(sorted(candidates))
    if key in memo:
        return memo[key]

    if len(candidates) == 0:
        return TreeNode(guess="???", is_leaf=True)
    if len(candidates) == 1:
        return TreeNode(guess=candidates[0], is_leaf=True)

    best_guess = None
    best_expected_remaining = float('inf')
    best_partitions = None

    for guess in candidates:
        partitions = partition_by_score(guess, candidates)

        # Compute expected remaining candidates after this guess
        # Weighted by probability of each outcome (assume uniform secret)
        total_remaining = 0
        for score, words in partitions.items():
            if score == 3:
                # Found it! Contributes 0 to remaining
                continue
            remaining = [w for w in words if w != guess]
            # Probability of this outcome = len(words) / len(candidates)
            # Expected remaining = sum over outcomes of (prob * remaining_size)
            total_remaining += len(remaining) * len(words)

        expected_remaining = total_remaining / len(candidates)

        if expected_remaining < best_expected_remaining:
            best_expected_remaining = expected_remaining
            best_guess = guess
            best_partitions = partitions

    if best_guess is None:
        best_guess = candidates[0]
        best_partitions = partition_by_score(best_guess, candidates)

    children = {}
    for score in range(4):
        if score in best_partitions:
            remaining = best_partitions[score]
            if score == 3:
                children[score] = TreeNode(guess=best_guess, is_leaf=True)
            else:
                remaining = [w for w in remaining if w != best_guess]
                if remaining:
                    children[score] = build_tree_min_average(remaining, memo)

    result = TreeNode(guess=best_guess, children=children)
    memo[key] = result
    return result


def build_tree_entropy(candidates: list[str], memo: dict = None) -> TreeNode:
    """
    Build tree using INFORMATION GAIN (entropy-based, like ID3/C4.5).
    Pick the guess that maximizes information gain = reduces entropy most.

    Entropy H = -Σ pᵢ log₂(pᵢ) where pᵢ is fraction in each partition.
    Information gain = H(before) - weighted average H(after).
    Since H(before) is constant for a given candidate set, we maximize
    by minimizing the weighted average entropy of partitions.
    """
    import math

    if memo is None:
        memo = {}

    key = tuple(sorted(candidates))
    if key in memo:
        return memo[key]

    if len(candidates) == 0:
        return TreeNode(guess="???", is_leaf=True)
    if len(candidates) == 1:
        return TreeNode(guess=candidates[0], is_leaf=True)

    def entropy(partition_sizes, total):
        """Compute entropy of a partition."""
        h = 0.0
        for size in partition_sizes:
            if size > 0:
                p = size / total
                h -= p * math.log2(p)
        return h

    best_guess = None
    best_info_gain = -float('inf')
    best_partitions = None

    # Current entropy (uniform distribution over candidates)
    n = len(candidates)
    h_before = math.log2(n)  # Entropy of uniform distribution

    for guess in candidates:
        partitions = partition_by_score(guess, candidates)

        # Compute weighted average entropy after this guess
        h_after = 0.0
        for score, words in partitions.items():
            if score == 3:
                # Found it! Entropy = 0 for this branch
                prob = 1 / n  # Probability we land here
                h_after += prob * 0
            else:
                remaining = [w for w in words if w != guess]
                if remaining:
                    prob = len(words) / n
                    # Entropy of this partition (uniform within partition)
                    h_partition = math.log2(len(remaining)) if len(remaining) > 1 else 0
                    h_after += prob * h_partition

        info_gain = h_before - h_after

        if info_gain > best_info_gain:
            best_info_gain = info_gain
            best_guess = guess
            best_partitions = partitions

    if best_guess is None:
        best_guess = candidates[0]
        best_partitions = partition_by_score(best_guess, candidates)

    children = {}
    for score in range(4):
        if score in best_partitions:
            remaining = best_partitions[score]
            if score == 3:
                children[score] = TreeNode(guess=best_guess, is_leaf=True)
            else:
                remaining = [w for w in remaining if w != best_guess]
                if remaining:
                    children[score] = build_tree_entropy(remaining, memo)

    result = TreeNode(guess=best_guess, children=children)
    memo[key] = result
    return result


def build_tree_worst(candidates: list[str]) -> TreeNode:
    """
    Build COMPLETE tree using WORST strategy: maximize worst-case depth.
    Simulates bad play that doesn't split well.
    """
    if len(candidates) == 0:
        return TreeNode(guess="???", is_leaf=True)
    if len(candidates) == 1:
        return TreeNode(guess=candidates[0], is_leaf=True)

    # Find guess that MAXIMIZES the maximum partition size (bad strategy!)
    worst_guess = None
    worst_max_partition = 0
    worst_partitions = None

    # Prefer guesses that don't discriminate well
    # Words with common letters like O tend to create bad splits
    trap_preference = ["mob", "jog", "nor", "woo", "soy", "oat", "oil"]

    for guess in candidates:
        partitions = partition_by_score(guess, candidates)
        max_size = 0
        for score, words in partitions.items():
            if score == 3:
                continue
            max_size = max(max_size, len(words))

        # Prefer trap words, then maximize partition size
        is_trap = guess in trap_preference
        current_score = (is_trap, max_size)
        best_so_far = (worst_guess in trap_preference if worst_guess else False, worst_max_partition)

        if current_score > best_so_far:
            worst_max_partition = max_size
            worst_guess = guess
            worst_partitions = partitions

    if worst_guess is None:
        worst_guess = candidates[0]
        worst_partitions = partition_by_score(worst_guess, candidates)

    # Build subtrees for each possible score
    children = {}
    for score in range(4):
        if score in worst_partitions:
            remaining = worst_partitions[score]
            if score == 3:
                children[score] = TreeNode(guess=worst_guess, is_leaf=True)
            else:
                remaining = [w for w in remaining if w != worst_guess]
                if remaining:
                    children[score] = build_tree_worst(remaining)

    return TreeNode(guess=worst_guess, children=children)


def tree_to_svg(node: TreeNode, title: str, strategy: str, width: int = 500, height: int = 600) -> str:
    """Convert complete decision tree to SVG visualization."""

    # First pass: compute positions using leaf-count-based layout
    # This ensures leaves get equal horizontal space and don't overlap
    positions = {}  # node_id -> (x, y)
    node_info = {}  # node_id -> (word, is_leaf)
    edges = []  # (parent_id, child_id, score)

    node_counter = [0]
    leaf_counter = [0]  # Track x position by counting leaves

    LEAF_WIDTH = 55  # Horizontal space per leaf

    # Count total leaves to compute width
    total_leaves = node.num_leaves()
    computed_width = max(width, total_leaves * LEAF_WIDTH + 40)

    def compute_layout(n: TreeNode, depth: int) -> tuple[int, float]:
        """Returns (node_id, x_center). Leaves get sequential x positions."""
        node_id = node_counter[0]
        node_counter[0] += 1

        y = 60 + depth * 80

        if n.is_leaf or not n.children:
            # Leaf: assign next available x slot
            x = 30 + leaf_counter[0] * LEAF_WIDTH + LEAF_WIDTH / 2
            leaf_counter[0] += 1
            positions[node_id] = (x, y)
            node_info[node_id] = (n.guess.upper(), True)
            return node_id, x

        # Internal node: position at center of children
        child_positions = []
        sorted_children = sorted(n.children.items())

        for score, child in sorted_children:
            child_id, child_x = compute_layout(child, depth + 1)
            edges.append((node_id, child_id, score))
            child_positions.append(child_x)

        x = sum(child_positions) / len(child_positions)
        positions[node_id] = (x, y)
        node_info[node_id] = (n.guess.upper(), False)

        return node_id, x

    compute_layout(node, 0)

    width = computed_width

    # Adjust height based on actual depth
    max_y = max(y for x, y in positions.values()) + 50
    actual_height = max(height, max_y)

    # Build SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{actual_height}" viewBox="0 0 {width} {actual_height}">',
        '<style>',
        '  .node-text { font-family: monospace; font-size: 11px; font-weight: bold; }',
        '  .edge-label { font-family: sans-serif; font-size: 9px; fill: #333; }',
        '  .title { font-family: sans-serif; font-size: 14px; font-weight: bold; }',
        '  .stats { font-family: sans-serif; font-size: 11px; fill: #666; }',
        '</style>',
        f'<rect width="{width}" height="{actual_height}" fill="white"/>',
    ]

    # Draw edges first (behind nodes)
    for parent_id, child_id, score in edges:
        x1, y1 = positions[parent_id]
        x2, y2 = positions[child_id]
        svg_parts.append(
            f'<line x1="{x1}" y1="{y1+12}" x2="{x2}" y2="{y2-12}" '
            f'stroke="#aaa" stroke-width="1.5"/>'
        )
        # Score label on edge
        mid_x = (x1 + x2) / 2 + 8
        mid_y = (y1 + y2) / 2
        svg_parts.append(f'<text x="{mid_x}" y="{mid_y}" class="edge-label">{score}</text>')

    # Draw nodes
    for node_id, (x, y) in positions.items():
        word, is_leaf = node_info[node_id]
        if is_leaf:
            fill = "#4CAF50"  # Green for leaves (answers)
            text_fill = "white"
            rx = "12"  # Rounded for leaves
        else:
            fill = "#2196F3"  # Blue for internal nodes (guesses)
            text_fill = "white"
            rx = "3"

        box_width = 40
        svg_parts.append(
            f'<rect x="{x - box_width/2}" y="{y-10}" width="{box_width}" height="20" '
            f'rx="{rx}" fill="{fill}"/>'
        )
        svg_parts.append(
            f'<text x="{x}" y="{y+4}" text-anchor="middle" class="node-text" fill="{text_fill}">'
            f'{html.escape(word)}</text>'
        )

    # Title and stats
    color = "#4CAF50" if strategy == "best" else "#f44336"
    svg_parts.append(f'<text x="{width/2}" y="25" text-anchor="middle" class="title" fill="{color}">{html.escape(title)}</text>')

    depth = node.depth()
    leaves = node.num_leaves()
    avg_depth = node.average_depth()
    svg_parts.append(f'<text x="{width/2}" y="{actual_height - 10}" text-anchor="middle" class="stats">Max depth: {depth} | Avg depth: {avg_depth:.2f} | Leaves: {leaves}</text>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def generate_html_gallery() -> str:
    """Generate HTML page comparing all strategies."""

    print("Building trees...")
    print("  - Greedy minimax (min max partition)...")
    greedy_tree = build_tree_minimax_greedy(WORDS.copy())

    print("  - True minimax (exhaustive search)...")
    true_minimax_tree = build_tree_true_minimax(WORDS.copy())

    print("  - Min average depth...")
    min_avg_tree = build_tree_min_average(WORDS.copy())

    print("  - Entropy/Information Gain (ID3-style)...")
    entropy_tree = build_tree_entropy(WORDS.copy())

    print("  - Worst strategy...")
    worst_tree = build_tree_worst(WORDS.copy())

    greedy_svg = tree_to_svg(greedy_tree, "Greedy Minimax (min max partition)", "best", 900, 600)
    true_minimax_svg = tree_to_svg(true_minimax_tree, "True Minimax (exhaustive)", "best", 900, 600)
    min_avg_svg = tree_to_svg(min_avg_tree, "Min Average Depth", "best", 900, 600)
    entropy_svg = tree_to_svg(entropy_tree, "Information Gain (ID3-style)", "best", 900, 600)
    worst_svg = tree_to_svg(worst_tree, "Worst Strategy (bad splits)", "worst", 900, 700)

    html_content = f'''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>Jotto Decision Trees - Strategy Comparison</title>
<style>
  body {{ font-family: sans-serif; max-width: 1800px; margin: 0 auto; padding: 20px; }}
  h1, h2 {{ text-align: center; }}
  .container {{ display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; margin-bottom: 40px; }}
  .tree {{ border: 2px solid #ddd; border-radius: 8px; padding: 15px; background: #fafafa; }}
  .tree h3 {{ text-align: center; margin: 0 0 10px 0; }}
  .legend {{ text-align: center; margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
  .legend span {{ margin: 0 15px; }}
  .blue {{ color: #2196F3; font-weight: bold; }}
  .green {{ color: #4CAF50; font-weight: bold; }}
  .comparison {{ max-width: 900px; margin: 30px auto; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
  th {{ background: #f5f5f5; }}
  .best-val {{ background: #c8e6c9; font-weight: bold; }}
  .worst-val {{ background: #ffcdd2; }}
  @media print {{
    .tree {{ page-break-inside: avoid; }}
  }}
</style>
</head><body>
<h1>Jotto Decision Trees: Strategy Comparison</h1>

<div class="legend">
  <span class="blue">■ Blue boxes</span> = Guess this word |
  <span class="green">■ Green rounded</span> = Answer (leaf) |
  <span>Edge labels</span> = Jotto score (0-3)
</div>

<div class="comparison">
<h2>Strategy Comparison</h2>
<table>
  <tr>
    <th>Strategy</th>
    <th>Max Depth (worst case)</th>
    <th>Avg Depth (expected)</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>Greedy Minimax</td>
    <td class="{'best-val' if greedy_tree.depth() <= true_minimax_tree.depth() else ''}">{greedy_tree.depth()}</td>
    <td class="{'best-val' if greedy_tree.average_depth() <= min(true_minimax_tree.average_depth(), min_avg_tree.average_depth(), entropy_tree.average_depth()) else ''}">{greedy_tree.average_depth():.2f}</td>
    <td>At each step, pick guess minimizing max partition size</td>
  </tr>
  <tr>
    <td>True Minimax</td>
    <td class="best-val">{true_minimax_tree.depth()}</td>
    <td class="{'best-val' if true_minimax_tree.average_depth() <= min(greedy_tree.average_depth(), min_avg_tree.average_depth(), entropy_tree.average_depth()) else ''}">{true_minimax_tree.average_depth():.2f}</td>
    <td>Exhaustive search for minimum worst-case depth</td>
  </tr>
  <tr>
    <td>Min Average</td>
    <td class="{'best-val' if min_avg_tree.depth() <= true_minimax_tree.depth() else ''}">{min_avg_tree.depth()}</td>
    <td class="{'best-val' if min_avg_tree.average_depth() <= min(greedy_tree.average_depth(), true_minimax_tree.average_depth(), entropy_tree.average_depth()) else ''}">{min_avg_tree.average_depth():.2f}</td>
    <td>Minimize expected remaining candidates</td>
  </tr>
  <tr>
    <td>Information Gain (ID3)</td>
    <td class="{'best-val' if entropy_tree.depth() <= true_minimax_tree.depth() else ''}">{entropy_tree.depth()}</td>
    <td class="{'best-val' if entropy_tree.average_depth() <= min(greedy_tree.average_depth(), true_minimax_tree.average_depth(), min_avg_tree.average_depth()) else ''}">{entropy_tree.average_depth():.2f}</td>
    <td>Maximize entropy reduction (ML decision trees)</td>
  </tr>
  <tr>
    <td>Worst Strategy</td>
    <td class="worst-val">{worst_tree.depth()}</td>
    <td class="worst-val">{worst_tree.average_depth():.2f}</td>
    <td>Deliberately bad: prefer trap clusters, max partitions</td>
  </tr>
</table>
</div>

<h2>Decision Trees</h2>

<div class="container">
  <div class="tree">
    <h3>Greedy Minimax</h3>
    {greedy_svg}
  </div>
  <div class="tree">
    <h3>True Minimax</h3>
    {true_minimax_svg}
  </div>
</div>

<div class="container">
  <div class="tree">
    <h3>Min Average Depth</h3>
    {min_avg_svg}
  </div>
  <div class="tree">
    <h3>Information Gain (ID3)</h3>
    {entropy_svg}
  </div>
</div>

<div class="container">
  <div class="tree">
    <h3>Worst Strategy</h3>
    {worst_svg}
  </div>
</div>

<h2>The 16 Words</h2>
<p style="text-align:center; font-family: monospace; font-size: 18px;">
  {" &nbsp; ".join(w.upper() for w in WORDS)}
</p>

<div class="comparison">
<h2>What's the difference?</h2>
<ul style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  <li><strong>Greedy Minimax</strong>: At each node, pick the guess that minimizes the <em>largest</em> remaining partition. Fast to compute, but only looks one level ahead.</li>
  <li><strong>True Minimax</strong>: Exhaustively try all possible guesses and recursively find the tree with minimum worst-case depth. Guarantees optimal worst case.</li>
  <li><strong>Min Average</strong>: Pick the guess that minimizes <em>expected</em> remaining candidates (weighted by probability). Optimizes for the average case, not worst case.</li>
  <li><strong>Information Gain (ID3)</strong>: Pick the guess that maximizes <em>information gain</em> — the reduction in entropy. This is what classic ML decision tree algorithms (ID3, C4.5) use. Entropy H = -Σ pᵢ log₂(pᵢ).</li>
  <li><strong>Worst Strategy</strong>: Deliberately picks guesses that don't discriminate well (words with common letter O). Shows what happens with bad strategy.</li>
</ul>
</div>

<div class="comparison">
<h2>Lower Bound: How good can we possibly be?</h2>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  Each guess produces one of <strong>4 possible outcomes</strong> (Jotto scores 0, 1, 2, or 3).
  A decision tree with 16 leaves needs enough internal nodes to distinguish all 16 words.
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  <strong>Information-theoretic lower bound:</strong> A perfect 4-way split at each level gives us
  4<sup>d</sup> leaves at depth d. To identify 16 words, we need at least:
</p>
<p style="text-align: center; font-size: 1.3em; margin: 20px 0;">
  4<sup>d</sup> ≥ 16 &nbsp;⟹&nbsp; d ≥ log<sub>4</sub>(16) = <strong>2</strong>
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  But wait — can we actually achieve depth 2? That would require our first guess to split
  the 16 words into 4 groups of exactly 4, and then each follow-up to split those 4 into
  singletons. Looking at the score matrix... <strong>no guess achieves a perfect 4-way split!</strong>
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  The best we can do is <strong>depth 4</strong> — twice the theoretical minimum. This gap shows
  that our word set has "entanglement" — words share letters in ways that prevent perfect discrimination.
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8; background: #fff3e0; padding: 15px; border-radius: 8px;">
  <strong>Student question:</strong> With 4 possible outcomes per guess and 16 words, why can't we
  always identify the word in 2 guesses? What property of the words prevents this?
</p>
</div>

<div class="comparison">
<h2>Connection to Machine Learning</h2>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  This Jotto game is exactly a <strong>classification problem</strong>! The connection:
</p>
<table style="max-width: 700px; margin: 20px auto;">
  <tr><th>ML Decision Tree</th><th>Jotto</th></tr>
  <tr><td>Classes to predict</td><td>The 16 possible secret words</td></tr>
  <tr><td>Features</td><td>Jotto scores against candidate words</td></tr>
  <tr><td>Split criterion</td><td>Which word to guess next</td></tr>
  <tr><td>Information gain</td><td>How much a guess tells us about the secret</td></tr>
  <tr><td>Leaf nodes</td><td>Final answer: "the secret is X"</td></tr>
</table>

<h3 style="text-align: center;">Computational Complexity</h3>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  Finding the <strong>optimal decision tree</strong> (minimum depth or size) is <strong>NP-hard</strong>!
  This was proven by Hyafil &amp; Rivest in 1976. Even approximating the minimum depth within a constant
  factor is hard.
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  That's why real-world ML systems (ID3, C4.5, CART, random forests) use <strong>greedy heuristics</strong>
  like information gain or Gini impurity — they're fast and usually produce good (if not optimal) trees.
</p>
<p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
  For our 16-word Jotto, exhaustive search is feasible. But for Wordle's 2,309 words?
  The search space explodes, and greedy methods become essential.
</p>
</div>

</body></html>'''

    return html_content


if __name__ == "__main__":
    html_content = generate_html_gallery()

    output_path = "/Users/cheeren/Repos/dsci221-root/dsci221/slides/jotto_trees.html"
    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"\nGenerated: {output_path}")

    # Summary
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)

    greedy = build_tree_minimax_greedy(WORDS.copy())
    true_mm = build_tree_true_minimax(WORDS.copy())
    min_avg = build_tree_min_average(WORDS.copy())
    entropy = build_tree_entropy(WORDS.copy())
    worst = build_tree_worst(WORDS.copy())

    print(f"\n{'Strategy':<25} {'Max Depth':<12} {'Avg Depth':<12}")
    print("-"*50)
    print(f"{'Greedy Minimax':<25} {greedy.depth():<12} {greedy.average_depth():<12.2f}")
    print(f"{'True Minimax':<25} {true_mm.depth():<12} {true_mm.average_depth():<12.2f}")
    print(f"{'Min Average':<25} {min_avg.depth():<12} {min_avg.average_depth():<12.2f}")
    print(f"{'Information Gain (ID3)':<25} {entropy.depth():<12} {entropy.average_depth():<12.2f}")
    print(f"{'Worst Strategy':<25} {worst.depth():<12} {worst.average_depth():<12.2f}")

    print(f"\nTheoretical lower bound: log_4(16) = 2 guesses")
    print(f"Actual best achievable:  {true_mm.depth()} guesses")
    print(f"Gap factor: {true_mm.depth() / 2:.1f}x")
