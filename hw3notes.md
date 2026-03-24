# HW3 Notes: Parking Problem + Path Compression

## Status
Not started. Design-phase notes from conversation on 2026-03-22.

---

## Context: Existing Question

The CPSC221 question (`hws/h3_2020W1_disjoint_sets/question.html`) already covers:
1. Best spot for first bus (answer: d_1, not 1 — parking as far as possible frees up nearby spots)
2. Reading the uptree: which spots are free?
3. Update rule: `simple_union(find(d-1), d)` after parking at d
4. Why **simple_union** (not size/rank): roots must be the minimum of their set (best available spot). Smart union would let an occupied node become root — breaking correctness.
5. Initialization: loop from A=0 to B=m
6. "No spot" sentinel: `find(d) == 0`
7. Runtime **without** path compression: Θ(m + n²)

The question originally had a commented-out follow-up:
> "If you replaced all find operations with path-compression ones, what would the worst-case runtime be?"
> Answer key: **Θ(m + n)**. Note: "This last question is tricky. It's a charging argument."

**Plan:** Uncomment and heavily scaffold this follow-up as a new section.

---

## Key Insight: Why Smart Union is Forever Off-Limits

`simple_union(find(d-1), d)` always makes `find(d-1) < d` the root — a still-available, lower-numbered spot. If we used size/rank union, the larger tree might win and make `d` (an occupied spot) the root. The key invariant breaks.

Therefore: **only path compression is available as an optimization.** Smart union is not applicable.

---

## The Runtime Argument

### Without path compression: Θ(m + n²)

Worst case: all buses want spot m. After k buses, `find(m)` traverses a chain of length k.
Find costs: 1, 2, 3, 4, ..., n → total = n(n+1)/2 = Θ(n²).
Plus Θ(m) initialization. Total: **Θ(m + n²)**.

### With path compression: Θ(m + n)

Same worst case (all buses want spot m). Find costs: **1, 2, 3, 3, 3, ..., 3**.
Total = 1 + 2 + 3(n−2) = Θ(n).

**Why it stabilizes at 3:**
After bus k's find, path compression makes `m` point directly to the current root.
The union then adds one hop (root → new root).
So `m` is always exactly 2 hops from root after any union — the find cost never grows.

### The amortized argument (potential function)

Let **Φ = sum of depths of all nodes** in the uptree.

**Amortized cost of a find with path length k:**

Nodes on the path (excluding root and its direct child) have depth ≥ 2.
Path compression sets them all to depth 1.

$$\Delta\Phi_{\text{find}} \leq -(k-2)$$

$$\text{amortized cost} = k + \Delta\Phi \leq k - (k-2) = \mathbf{2}$$

Every find has amortized cost ≤ 2, regardless of path length.

Since Φ ≥ 0 always, total actual cost ≤ Σ amortized ≤ 2 × (# finds) + union costs.
Union and initialization costs are Θ(m + n). **Total: Θ(m + n).**

**Note:** The formal proof (accounting for Φ increases from unions) is subtle — both Σ(amortized) and Φ_final can be Θ(n²) in the worst case, but their *difference* is Θ(n). The CPSC221 key calls this "tricky — it's a charging argument." For students, the amortized-per-find argument captures the key insight; the full formal proof is beyond scope.

---

## Concrete Trace (Answer Key)

Setup: m = 7 (spots 0–7, spot 0 is sentinel). 6 buses, all wanting spot 7.

| Bus | find(7) path | find cost | PC result | Union |
|-----|-------------|-----------|-----------|-------|
| 1 | `7` | 1 | — | 7→6 |
| 2 | `7→6` | 2 | (7 stays at depth 1) | 6→5 |
| 3 | `7→6→5` | 3 | 7→5, 6→5 | 5→4 |
| 4 | `7→5→4` | 3 | 7→4, 5→4 | 4→3 |
| 5 | `7→4→3` | 3 | 7→3, 4→3 | 3→2 |
| 6 | `7→3→2` | 3 | 7→2, 3→2 | 2→1 |

Without PC, costs would be: 1, 2, 3, 4, 5, 6 → Θ(n²) total.
With PC: 1, 2, 3, 3, 3, 3 → Θ(n) total.

**Note on node 6 (a subtlety worth showing students):**
After bus 3: 6→5→4. After bus 4's find(7) path is `7→5→4`, node 6 is *not* on this path and is NOT compressed. After bus 4's union (5→4→3): node 6 has depth 3 (6→5→4→3). If someone queried `find(6)` at this point, it would cost 4. This is fine — if no one queries 6, it never costs anything.

---

## Planned New Section Structure

**Opening:** "We now modify our algorithm: every `find` call uses **path compression** — after finding the root, every node on the path is updated to point directly to the root."

**Part A: Trace (heavily scaffolded)**
- Give the table above with rows 4–6 blank
- Include uptree diagrams for buses 1–3 as worked examples (SVG or image)
- Ask students to fill in rows 4–6
- Follow-up: "What do you notice about the find cost starting from bus 3?"

**Part B: Contrast**
- "Without PC, what would the find cost be for bus k?" (answer: k)
- "Fill in the total find cost for n buses, with and without PC" (n² vs Θ(n))

**Part C: Why it stabilizes (conceptual)**
- "After bus 3 parks, node 7 points directly to the new root (5). Draw the uptree."
- "After bus 4's union (5→4), what is the depth of node 7?"
- "After bus 4's find(7), what is the depth of node 7?"
- "Explain in one sentence why find(7) always costs exactly 3 from bus 3 onward."

**Part D: Amortized argument (most scaffolded part)**
- Define Φ = sum of depths. Walk through Φ values for buses 1–4 step by step.
- Give the formula: amortized cost = actual cost + ΔΦ.
- Worked example: bus 3's find, actual cost = 3, ΔΦ = −1, amortized = 2.
- "Compute amortized cost for bus 4's find."
- "For a find of path length k, the deepest k−2 nodes all get compressed from depth ≥ 2 to depth 1. What is ΔΦ? What is the amortized cost?"
- "Since Φ ≥ 0 always, we know total actual ≤ Σ amortized ≤ ___. Conclude the total find cost is Θ(_____)."

**Part E: Final answer**
- Multiple choice: Θ(m+n), Θ(m+n log* n), Θ(m+n log n), Θ(m+n²), Θ(m log n)
- Answer: **Θ(m + n)**

---

## Scaffolding Notes

- "Just reading it will be hard for them" — every conceptual step needs to be broken into a fill-in or forced observation.
- Uptree diagrams are essential. Students need to *see* the tree flatten.
- The ΔΦ calculation should be a worked example before students are asked to compute it themselves.
- The leap from "amortized ≤ 2 per find" to "total is O(n)" needs to be spelled out: "there are Θ(n) total find calls, each costing ≤ 2 amortized, so total ≤ ___."
- Optionally: include a note that the proof for arbitrary input sequences (not just all-want-m) uses the same amortized argument, but the formal accounting is more involved.

---

## Related Files
- Existing question: `pl-ubc-cpsc221/questions/hws/h3_2020W1_disjoint_sets/question.html`
- Target assessment: `dsci221-prairielearn/courseInstances/2025W2/assessments/homework/hw_03/` (to be created)
