# Model Card — Game Glitch Investigator: Agentic Self-Healing System

## Model / System Identity

**System name** | Agentic Self-Healing System (`agentic_fixer.py`) 
**Base project** | Game Glitch Investigator: The Impossible Guesser (Modules 1–3) 
**AI model used** | `qwen2.5-coder:7b` via Ollama (local inference, no external API) 
**Framework** | Python 3.10+, pytest, subprocess, Streamlit 
**Author** | Benjamin Hanbaly 

## Purpose

This system automates a debugging feedback loop. It runs a pytest suite against a target Python file, sends any failures alongside the source code to a local code-generation model, applies the model's fix, and re-runs the tests - repeating up to three times. The goal is to demonstrate an agentic pattern in which an AI model performs repair work within boundaries defined entirely by human-written tests.

## AI Collaboration

### How AI was used in this project

AI (Claude) was used as a collaborative coding partner across both phases of the project: the original bug-fixing exercise (Modules 1–3) and the agentic system design (Module 4).

In the original project, Claude helped identify bugs, suggest fixes, and write targeted pytest cases. In Module 4, Claude assisted in designing the loop architecture, writing the prompt sent to `qwen2.5-coder:7b`, and adding the `_strip_code_fences` helper after the model repeatedly returned markdown-wrapped output.

### Helpful suggestion

When debugging the off-by-one error in the game, Claude identified that `st.session_state.attempts` was initialized to `1` instead of `0`, causing every game to start with one guess already consumed. The explanation connected the value directly to the observed symptom — players always losing one guess on their very first game — rather than just pointing at the line number. That cause-and-effect framing made the fix straightforward to verify: play a game, count the attempts, confirm they matched the difficulty limit.

### Flawed suggestion

When asked to fix the Hard difficulty range (which was incorrectly set to `1–50`, making it easier than Normal's `1–100`), Claude returned `1200` as the upper bound. The correct fix was `200`. The suggestion was syntactically valid and would have passed any test checking only that the hard range exceeded 100, but it did not match the intent. This illustrates a consistent risk with AI-generated code: the output can be plausible and even test-passing while still being semantically wrong relative to the specification. Reviewing AI output against original intent - not just test results - is essential.

## Known Limitations and Biases

**Test coverage ceiling.** The loop can only verify what the tests check. A bug in an untested code path is invisible to the system - the model could silently introduce or preserve it while the suite reports green. The system's reliability is directly proportional to the completeness of the test suite.

**No cross-attempt memory.** Each cycle sends the full file and error log from scratch. The model has no awareness of what it changed on the previous attempt, so it can oscillate between two broken states rather than making monotonic progress toward a fix.

**Model size limits.** `qwen2.5-coder:7b` handles small, well-scoped functions reliably. On larger files with subtle inter-function dependencies, it will miss bugs or introduce regressions. The system is designed for files under ~100 lines with well-isolated logic.

**Single-error focus.** When multiple tests fail simultaneously, the model tends to address whichever error appears first in the pytest output and ignore the rest. Multi-bug convergence requires multiple loop iterations.

**Prompt-format sensitivity.** The model occasionally ignores the instruction to return code only and wraps output in markdown fences anyway. This is handled by `_strip_code_fences()`, but it reflects a broader limitation: models do not reliably follow formatting constraints, and output parsing must be defensive.

## Potential for Misuse

An autonomous file-overwriting loop is a high-trust tool. Risks include:

- **Silent security degradation:** If a codebase has gaps in test coverage for security-critical paths (input validation, authentication checks), the model could weaken those paths while passing all existing tests.
- **Runaway edits on large files:** Without the 3-attempt cap, a model that cannot converge would loop indefinitely, producing a succession of broken files with each backup overwritten by the next.

**Existing guardrails in this system:**
- Every overwrite is backed up before it happens (`.bak1`, `.bak2`, `.bak3`), making all AI edits reversible and diffable.
- The loop fails loudly with a `RESULT: FAILED` log entry when it cannot converge, rather than silently accepting a broken state.
- The model never touches the test files - it can only modify the target source file, so it cannot rewrite the specification it is supposed to satisfy.

**What a production version should add:**
- Human approval step before each overwrite
- Scope restriction: model is only allowed to rewrite functions that have direct test coverage
- Output validation: parse the model's response as an AST before writing it to disk, rejecting syntactically invalid code immediately

## Testing Results

### Automated test suite

```
pytest tests/test_game_logic.py -v
15 passed in 0.17s
```

`check_guess` | 5 checks | Reversed high/low hints; string-cast type mismatch on even attempts |
`update_score` | 5 checks | +5 awarded instead of −5 for wrong guesses on even attempts |
`parse_guess` | 5 checks | None and empty string not rejected; float inputs caused TypeError |

All 15 tests were written to **fail first** against the original broken code and **pass only after** the correct fix was applied. This confirmed each test was exercising real behavior, not passing vacuously.

### Agentic loop reliability

Scenario | Attempts to converge | Outcome 

No bugs present | 1 (exits immediately) | SUCCESS — model never called 
Single-function bug | 2 (1 fix + 1 verify) | SUCCESS 
Two simultaneous bugs | 3 (2 fix cycles + 1 verify) | SUCCESS 
Model returns markdown-fenced output | Handled silently by `_strip_code_fences()` | No failure 

### What worked

The pytest-as-ground-truth architecture was the right call. The model could not cheat by rewriting tests - it had to fix the logic. Single-bug files were repaired reliably on the first attempt. The timestamped log made it easy to audit exactly what the AI did on each cycle.

### What didn't work

When two unrelated bugs existed simultaneously, the model fixed only one per attempt. This is a real limitation rather than an implementation bug: the model reads one dominant error and solves it, then needs to see the remaining failure in the next cycle. It means the 3-attempt cap is load-bearing for multi-bug scenarios.

### What I learned

Tests are the most important part of an agentic system. The AI is only as reliable as the specification you give it. A model operating within a thorough test suite becomes a fast, trustworthy repair tool. The same model operating without one becomes a source of plausible-looking but unverifiable changes. Writing tests first is not optional.

## What This Project Says About Me as an AI Engineer

I don't just use AI tools - I think carefully about where they break down. This project started as a debugging exercise and evolved into a system that automates the debugging loop itself, but the most important design decision was choosing not to let the AI define correctness. The human-written test suite is the specification; the model is the repair mechanic. Building the guardrails, audit trails, and failure modes make AI behavior trustworthy enough to run without constant supervision.
