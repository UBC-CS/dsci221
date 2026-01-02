# DSCI 221 TODO

## Completed Setup (Reference for Future Terms)

### GitHub Pages Deployment
- [x] Update README.md with course info (DSCI 221, not CPSC 203)
- [x] Fix GitHub Actions workflow to install R packages directly (renv had macOS-specific binaries that failed on Linux runners)
- [x] Install R dependencies: tidyverse, gt, gtExtras, fontawesome, here, conflicted, glue
- [x] Add knitr and rmarkdown to R dependencies
- [x] Set R_LIBS_USER for Quarto to find packages
- [x] Use `R --vanilla` to bypass renv activation

### Website Configuration
- [x] Update `_variables.yml` with course details (code, title, term, instructor, URLs)
- [x] Update `_quarto.yml` with correct repo URL and site URL
- [x] Update `about.qmd` with course description
- [x] Update `syllabus.qmd` with policies and grading
- [x] Create welcome announcement in `posts/00_welcome/index.qmd`

### Schedule Table (index.qmd)
- [x] Fix deprecated `cur_data()` → `pick(everything())` (dplyr 1.1.0+)
- [x] Add explicit column types to `read_csv()` to avoid parsing warnings
- [x] Ensure `schedule.csv` has correct number of fields per row (14 columns)
- [x] Convert `schedule.csv` to Unix line endings (LF, not CRLF)

### Curriculum Planning
- [x] Create detailed curriculum plan in `~/.claude/plans/` with:
  - 12-week course arc
  - Weekly puzzles and themes
  - Slide-by-slide outline for Week 1
  - Lab/PA/HW alignment
  - Rigor checklist matching CPSC 221 depth
- [x] Create Week 1 slides (Mon/Tue/Wed) in `slides/` directory

---

## Course Setup (Canvas/Infrastructure)
- [ ] Schedule class Zoom meetings in Canvas
- [ ] Set up appointment service for office hours (also in Canvas)

## Assessments

### Labs
- [ ] Create labs (major project)
  - Week 1: Timing experiments — predict, measure, explain
  - Week 2: Binary search implementation with invariant debugging
  - Week 3: Fractal image generation (Koch snowflake, Sierpinski)
  - Week 4: DFS vs BFS maze visualization
  - Week 5: Dictionary "aha!" puzzles
  - Week 6: Closest pair / sorting applications
  - Week 8: Wordle decision tree analysis
  - Week 9: Trending hashtags tracker
  - Week 10: Kevin Bacon oracle + Union-Find connectivity
  - Week 11: Cheapest flights with Dijkstra
  - Week 12: Exam scheduler with graph coloring

### Programming Assignments (PAs)
- [ ] Create programming assignments
  - PA1 (Week 5): Recursive art generator (L-systems or fractal landscapes)
  - PA2 (Week 9): Real-time event ranking system
  - PA3 (Week 12): Graph algorithms (BFS/Dijkstra application)

### Homework (HWs)
- [ ] Create homework assignments
  - HW1 (Week 3): Big-O proofs, loop invariants
  - HW2 (Week 6): Recurrences, dictionary puzzles, sorting analysis
  - HW3 (Week 14): Graph proofs, Dijkstra analysis

### Examlets
- [ ] Create examlets
  - PEX1-5: Practice examlets
  - EX1-5: Examlets
  - PEXF: Final practice examlet

### Practice Problems
- [ ] Create practice problems for each topic

## Technical Infrastructure
- [ ] Set up testing framework within marimo
- [ ] Set up autograder for PL programming assignments
