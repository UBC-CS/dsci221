# DSCI 221: Topical Schedule

**Term:** 2025 Winter Term 2 (January–April 2026)

## Course Overview

This course introduces fundamental data structures and algorithms through the lens of data science applications. Topics include sorting, searching, recursion, hash tables, trees, heaps, and graphs.

---

## Schedule Summary

### Part 1: Foundations (Weeks 1–4)
*How do we measure "fast"? Recursion as a problem-solving superpower.*

| Week | Dates | Topics | Assessments |
|------|-------|--------|-------------|
| 1 | Jan 5–9 | **The Speed of Thought**: Algorithm analysis, Big-O notation, loop analysis | — |
| 2 | Jan 12–16 | **Searching for Answers**: Loop invariants, correctness proofs, binary search | Lab 1 |
| 3 | Jan 19–23 | **The Recursion Revelation**: Recursive thinking, structural induction, recurrence relations | HW1 due (Sun) |
| 4 | Jan 26–30 | **Sorting as Superpower**: Merge sort, recurrence solving, sorting lower bounds | EX1 (Thu) |

### Part 2: Lookup & Order (Weeks 5–8)
*Dictionary magic and the stack/queue mindset.*

| Week | Dates | Topics | Assessments |
|------|-------|--------|-------------|
| 5 | Feb 2–6 | **The Dictionary Trick**: Hash tables, O(1) lookup, two-sum problem | PA1 due (Sun) |
| 6 | Feb 9–13 | **Stacks, Queues, and Mazes**: DFS vs BFS, maze solving, ADT specifications | EX2 (Thu), HW2 due (Sun) |
| 7 | Feb 16–20 | **Reading Week** | — |
| 8 | Feb 23–27 | **Trees as Recursive Structures**: Binary trees, BSTs, balanced trees | — |

### Part 3: Connections (Weeks 9–12)
*When data has relationships: graphs, paths, and the limits of computation.*

| Week | Dates | Topics | Assessments |
|------|-------|--------|-------------|
| 9 | Mar 2–6 | **Priority Queues**: Heaps, top-k problems, heapsort | EX3 (Thu), PA2 due (Sun) |
| 10 | Mar 9–13 | **Graphs I**: Graph representations, BFS, DFS, Union-Find | — |
| 11 | Mar 16–20 | **Graphs II**: Weighted graphs, Dijkstra's algorithm | EX4 (Thu) |
| 12 | Mar 23–27 | **Optimization & Limits**: MST, graph coloring, P vs NP | PA3 due (Sun) |
| 13 | Mar 30–Apr 3 | **Course Synthesis**: Choosing data structures, review | EX5 (Thu) |
| 14 | Apr 6–10 | Easter / Wrap-up | HW3 due (Sun) |

---

## Detailed Topic Outline

### Week 1: The Speed of Thought
*Puzzle: How does Shazam identify a song from 3 seconds of audio, searching millions of songs?*

- Why algorithm efficiency matters at scale
- Counting operations, parameterizing by input size
- Big-O, Big-Omega, Big-Theta: formal definitions
- Analyzing loops: linear, nested, triangular
- The complexity hierarchy: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ)

### Week 2: Searching for Answers
*Puzzle: I'm thinking of a number between 1 and 1,000,000. How few guesses do you need?*

- Loop invariants: Initialization, Maintenance, Termination
- Proving algorithm correctness
- Binary search: the power of sorted data
- Best, worst, and average case analysis

### Week 3: The Recursion Revelation
*Puzzle: Why is the coastline of Britain infinitely long?*

- Self-similarity and recursive thinking
- Recursive definitions: lists, trees
- Structural induction
- Introduction to recurrence relations

### Week 4: Sorting as Superpower
*Puzzle: Find the two most similar faces among 10 million photos.*

- Merge sort: divide and conquer
- Recurrence relations: T(n) = 2T(n/2) + O(n)
- Solving recurrences: expansion, recursion trees
- The comparison sorting lower bound: Ω(n log n)

### Week 5: The Dictionary Trick
*Puzzle: Given 1 million numbers, find two that sum to exactly 2024.*

- The O(n²) → O(n) transformation
- Hash tables and O(1) average-case lookup
- Dictionary patterns: "Have I seen this before?"
- Hash functions and collision handling (conceptual)

### Week 6: Stacks, Queues, and Mazes
*Puzzle: You wake up in a maze. How do you guarantee finding the exit?*

- Abstract Data Types (ADTs)
- Stacks: LIFO, DFS maze solving, call stack
- Queues: FIFO, BFS maze solving, shortest paths
- Comparing DFS and BFS

### Week 8: Trees as Recursive Structures
*Puzzle: What's the optimal first guess in Wordle?*

- Binary trees as recursive structures
- Tree traversals: preorder, inorder, postorder
- Binary Search Trees: insert, find, delete
- Balanced trees: the O(log n) guarantee (conceptual)

### Week 9: Priority Queues
*Puzzle: Track the top 10 trending hashtags from 500 million daily tweets.*

- Priority queue ADT
- Heaps: structure and heap property
- Heap operations: insert, extract-min, heapify
- Top-k problems, heapsort

### Week 10: Graphs I
*Puzzle: What's the shortest path from any actor to Kevin Bacon?*

- Graph terminology: vertices, edges, directed/undirected
- Representations: adjacency list vs adjacency matrix
- BFS: shortest paths in unweighted graphs
- DFS: exploring and backtracking
- Union-Find: dynamic connectivity

### Week 11: Graphs II
*Puzzle: Find the cheapest flight from Vancouver to Tokyo.*

- Weighted graphs
- Dijkstra's algorithm
- Priority queue implementation
- Correctness proof

### Week 12: Optimization and Limits
*Puzzle: Schedule 500 final exams so no student has two at once.*

- Minimum Spanning Trees: Prim's algorithm
- Graph coloring and NP-completeness
- P vs NP (conceptual)
- When "good enough" is good enough

---

## Assessment Schedule

| Assessment | Topics | Due/Date |
|------------|--------|----------|
| HW1 | Big-O, loop invariants | Week 3 Sunday |
| EX1 | Analysis, loop invariants, recursion | Week 4 Thursday |
| PA1 | Divide-and-conquer (closest pair) | Week 5 Sunday |
| HW2 | Recurrences, dictionaries, sorting | Week 6 Sunday |
| EX2 | Stacks, queues, dictionaries | Week 6 Thursday |
| PA2 | Heap-based application | Week 9 Sunday |
| EX3 | Trees, heaps | Week 9 Thursday |
| EX4 | Graphs, Dijkstra | Week 11 Thursday |
| PA3 | Graph algorithms | Week 12 Sunday |
| EX5 | Comprehensive | Week 13 Thursday |
| HW3 | Graphs, shortest paths | Week 14 Sunday |
