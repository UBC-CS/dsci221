# Marimo Grading Framework Analysis & Improvement Proposals

## Executive Summary

This document analyzes the current marimo notebook grading architecture used in DSCI 221 and CPSC 203, identifies pain points, and proposes improvements.

**Key Finding**: The current approach fights against marimo's design rather than working with it. Marimo has built-in testing support via pytest that we're not leveraging.

---

## Current Architecture

### How It Works Today

1. **Student writes code** in a marimo notebook (`workbook.py`)
2. **Grader Docker image** (`stephankoenig/marimo-grader:marimo-0.16.4`) runs PrairieLearn's Python autograder
3. **PrairieLearn extracts functions** from the notebook file as Python module attributes
4. **Test cases** in `test.py` call student functions via `Feedback.call_user(self.st.function_name, args)`
5. **Results compared** against reference solutions in `ans.py`

### Key Files Structure
```
question/
├── info.json              # Docker image, grading config
├── question.html          # Problem statement
├── workspace/
│   └── workbook.py        # Student's marimo notebook
└── tests/
    ├── test.py            # Test cases (PLTestCase)
    ├── ans.py             # Reference solutions
    ├── setup_code.py      # Runs before loading code
    └── leading_code.py    # Injected before student code (CRITICAL)
```

### The `leading_code.py` Workaround

CPSC 203 questions include this file:
```python
__name__ = "__main__"
```

This fixes the `KeyError: '__name__'` error by providing the variable that marimo notebooks expect when they execute. **PA1 was missing this file.**

---

## Pain Points Identified

### 1. Function Isolation Problem
**Symptom**: `closest_pair_recursive` can't call `squared_distance`

**Root Cause**: PrairieLearn extracts each `@app.function` as a standalone function object. They don't share a global namespace.

**Current Workaround**: Inject gold code helpers via `__globals__` in test `setUp()`:
```python
def inject_helpers(func, helpers_dict):
    if hasattr(func, '__globals__'):
        func.__globals__.update(helpers_dict)
```

**Problems with this approach**:
- Test author must manually track all dependencies
- Students can't test their own code locally the same way
- Fragile—depends on Python internals

### 2. The `__name__` KeyError
**Symptom**: `KeyError: '__name__'` when grader runs

**Root Cause**: Marimo notebooks check `if __name__ == "__main__"` to run `app.run()`. When imported as a module, `__name__` isn't `"__main__"` but PrairieLearn's loading mechanism doesn't provide it correctly.

**Current Workaround**: `leading_code.py` with `__name__ = "__main__"`

### 3. Purity Requirements Not Enforced
**Issue**: `@app.function` requires "pure" functions—they can only reference:
- Other `@app.function` decorated functions
- Imports and constants from `with app.setup:`

Students don't understand this constraint and write code that works in the notebook but fails in the grader.

### 4. Duplicated Logic
**Issue**: Reference implementations exist in both:
- `ans.py` (for comparison)
- `test.py` (as `_gold_*` functions for injection)

This violates DRY and creates maintenance burden.

### 5. No Local Testing Parity
**Issue**: Students can't run the same tests locally that the grader runs. They discover issues only after submission.

---

## Marimo's Native Testing Support

### What Marimo Offers (That We're Ignoring)

From [marimo's testing docs](https://docs.marimo.io/guides/testing/pytest/):

1. **Pytest integration**: Name cells `test_*` and run `pytest workbook.py`
2. **Fixtures in `app.setup`**: Define pytest fixtures in the setup block
3. **Automatic test discovery**: marimo finds `test_*` functions and `Test*` classes
4. **Cell isolation**: Only test cells run, not the whole notebook

**Example marimo test cell**:
```python
@app.cell
def test_squared_distance(squared_distance):
    assert squared_distance((0, 0), (3, 4)) == 25
    assert squared_distance((1, 1), (1, 1)) == 0
```

### Key Insight
> "If a cell mixes in anything else (helper functions, constants, variables, imports, etc.), that cell is skipped by the test runner."

This means we can embed tests directly in the student notebook that:
1. Run locally via `pytest workbook.py`
2. Get extracted and run by the grader

---

## Proposed Improvements

### Option A: Embrace Marimo's Testing (Recommended)

**Concept**: Put tests IN the notebook, use marimo's native pytest support.

**Structure**:
```python
import marimo
app = marimo.App()

with app.setup:
    import pytest
    # Any shared imports/fixtures

@app.function
def squared_distance(p1, p2):
    """Student implements this."""
    pass

@app.cell
def test_squared_distance_basic(squared_distance):
    """This cell IS a test—runs with pytest."""
    assert squared_distance((0, 0), (3, 4)) == 25

@app.cell
def test_squared_distance_same_point(squared_distance):
    assert squared_distance((5, 5), (5, 5)) == 0
```

**Benefits**:
- Students run exact same tests locally: `pytest workbook.py`
- No function isolation issues—marimo handles dependencies
- No `__globals__` injection hacks
- Test cells can use any function defined in the notebook

**Grader Changes Needed**:
- Run `pytest workbook.py` instead of custom test harness
- Parse pytest output for scores
- Map test names to point values (via markers or config)

**Challenges**:
- Need to prevent students from modifying test cells
- Partial credit scoring needs thought
- Integration with PrairieLearn's feedback display

### Option B: Improved Injection Framework

**Concept**: Keep current architecture but make it more robust and DRY.

**Changes**:
1. **Auto-generate `leading_code.py`** with `__name__ = "__main__"`
2. **Single source of truth** for gold implementations (just `ans.py`)
3. **Declarative dependency specification**:
   ```python
   class Test(PLTestCase):
       dependencies = {
           'closest_pair_brute': ['squared_distance'],
           'closest_in_strip': ['squared_distance'],
           'closest_pair_recursive': ['squared_distance', 'closest_pair_brute', 'closest_in_strip'],
       }
   ```
4. **Auto-inject in base class** `setUp()` based on declarations
5. **Better error messages** when dependencies are missing

**Implementation**:
```python
class MarimoTestCase(PLTestCase):
    """Base class that handles marimo function dependencies."""

    dependencies = {}  # Override in subclass

    def setUp(self):
        super().setUp()
        for func_name, deps in self.dependencies.items():
            if hasattr(self.st, func_name):
                helpers = {dep: getattr(self.ref, dep) for dep in deps}
                inject_helpers(getattr(self.st, func_name), helpers)
```

### Option C: Hybrid Approach

**Concept**: Use marimo's test discovery but keep external grading for scoring.

1. **Notebook contains test cells** (for local development)
2. **Grader runs pytest** on the notebook
3. **`conftest.py`** in tests/ provides:
   - Point values via `@pytest.mark.points(5)`
   - Gold implementations as fixtures
   - Custom output formatting for PrairieLearn

**Example `conftest.py`**:
```python
import pytest
from ans import squared_distance as gold_squared_distance

@pytest.fixture
def gold_squared_distance_fixture():
    return gold_squared_distance

def pytest_configure(config):
    config.addinivalue_line("markers", "points(n): assign point value to test")
```

---

## Immediate Fixes for PA1

While we design a better system, these fixes will make PA1 work:

### 1. Add `leading_code.py`
```python
# tests/leading_code.py
__name__ = "__main__"
```

### 2. Keep the injection approach (already done)
The current `inject_helpers` in `test.py` works, just needs the `leading_code.py` fix.

### 3. Document the pattern
Add comments explaining why this is necessary so future maintainers understand.

---

## Comparison Matrix

| Aspect | Current | Option A (Native) | Option B (Improved) | Option C (Hybrid) |
|--------|---------|-------------------|---------------------|-------------------|
| Local test parity | ❌ | ✅ | ❌ | ✅ |
| Dependency handling | Manual | Automatic | Declarative | Automatic |
| Maintenance burden | High | Low | Medium | Medium |
| Student UX | Poor | Excellent | Poor | Good |
| Implementation effort | Done | High | Medium | Medium |
| PrairieLearn integration | Native | Custom | Native | Custom |

---

## Recommendation

**Short term**: Fix PA1 with `leading_code.py` + current injection (already done).

**Medium term**: Implement Option B (improved injection) as a shared base class that both DSCI 221 and CPSC 203 can use.

**Long term**: Move toward Option A or C to give students local testing parity and reduce maintenance.

---

## Questions to Discuss

1. **Do we control the marimo-grader Docker image?** If so, we could add pytest and custom scoring output.

2. **How important is preventing test modification?** Marimo lets students see/edit all cells.

3. **Can we use PrairieLearn's `serverFilesCourse`** to share a common `MarimoTestCase` base class across all questions?

4. **Should tests be visible to students?** Pros: transparency, local testing. Cons: teaching to the test.

5. **What's the timeline?** Option A is best but needs most work.

---

## Resources

- [Marimo Testing Docs](https://docs.marimo.io/guides/testing/)
- [Marimo pytest Guide](https://docs.marimo.io/guides/testing/pytest/)
- [PrairieLearn Python Grader](https://github.com/PrairieLearn/PrairieLearn/blob/master/docs/python-grader/index.md)
- [@app.function docs](https://docs.marimo.io/guides/reusing_functions/)
- [app.function GitHub issue](https://github.com/marimo-team/marimo/issues/2293)
