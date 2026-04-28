"""
agentic_fixer.py — Agentic Self-Healing System
-----------------------------------------------
Runs pytest, sends failures + source code to qwen2.5-coder:7b via Ollama,
applies the model's fix, and repeats up to MAX_ATTEMPTS times.

Usage:
    python agentic_fixer.py [target_file]

    target_file  Path to the Python file to repair (default: logic_utils.py)
"""

import os
import sys
import subprocess
from datetime import datetime

import ollama

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET_FILE = sys.argv[1] if len(sys.argv) > 1 else "logic_utils.py"
TEST_COMMAND = [sys.executable, "-m", "pytest", "tests/test_game_logic.py", "-v", "--tb=short"]
LOG_FILE = "fix_history.log"
MAX_ATTEMPTS = 3
MODEL = "qwen2.5-coder:7b"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(message: str) -> None:
    """Print and append a timestamped entry to fix_history.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ---------------------------------------------------------------------------
# THE TESTER
# ---------------------------------------------------------------------------

def run_tests() -> tuple[bool, str]:
    """
    Run pytest and return (passed, full_output).
    `passed` is True only when pytest exits with code 0.
    """
    result = subprocess.run(
        TEST_COMMAND,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    output = result.stdout + result.stderr
    return result.returncode == 0, output


# ---------------------------------------------------------------------------
# THE WRITER
# ---------------------------------------------------------------------------

def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences that the model may wrap its output in."""
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def ask_model_to_fix(source_code: str, error_log: str) -> str:
    """
    Send the broken source file and pytest output to qwen2.5-coder:7b.
    Returns the corrected source code as a plain string.
    """
    prompt = (
        "You are an expert Python debugger.\n"
        "The file below is failing its pytest tests. "
        "Study the error output carefully, then return the COMPLETE corrected "
        "Python source code — nothing else. No explanations, no markdown, "
        "no commentary. Only valid Python.\n\n"
        f"### FILE: {TARGET_FILE}\n"
        "```python\n"
        f"{source_code}\n"
        "```\n\n"
        "### PYTEST FAILURE OUTPUT\n"
        "```\n"
        f"{error_log}\n"
        "```\n\n"
        "Return ONLY the corrected Python code:"
    )

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.message.content
    return _strip_code_fences(raw)


# ---------------------------------------------------------------------------
# THE LOOP
# ---------------------------------------------------------------------------

def healing_loop() -> None:
    """
    Core agentic loop:
      1. Run tests.
      2. If failing, read source → ask model → overwrite file.
      3. Repeat up to MAX_ATTEMPTS times.
      4. Log every step to fix_history.log.
    """
    log("=" * 62)
    log(f"Agentic Self-Healing System — start")
    log(f"Target file : {TARGET_FILE}")
    log(f"Test command: {' '.join(TEST_COMMAND)}")
    log(f"Model       : {MODEL}")
    log(f"Max attempts: {MAX_ATTEMPTS}")
    log("=" * 62)

    if not os.path.exists(TARGET_FILE):
        log(f"ERROR: Target file '{TARGET_FILE}' not found. Aborting.")
        sys.exit(1)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        log(f"\n>>> Attempt {attempt}/{MAX_ATTEMPTS}")

        # ── Step 1: Run the tests ──────────────────────────────────────────
        passed, test_output = run_tests()

        if passed:
            log("All tests PASSED. No repair needed.")
            log(f"RESULT: SUCCESS on attempt {attempt}")
            return

        log(f"Tests FAILED. Pytest output:\n{test_output}")

        # ── Step 2: Read current source ────────────────────────────────────
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            source_code = f.read()

        # ── Step 3: Ask the model for a fix ───────────────────────────────
        log(f"Sending to {MODEL} via Ollama…")
        try:
            fixed_code = ask_model_to_fix(source_code, test_output)
        except Exception as exc:
            log(f"ERROR: Ollama call failed — {exc}")
            log("RESULT: ABORTED (model unavailable)")
            sys.exit(1)

        if not fixed_code.strip():
            log("WARNING: Model returned an empty response. Skipping overwrite.")
            continue

        # ── Step 4: Back up original, then overwrite ───────────────────────
        backup_path = f"{TARGET_FILE}.bak{attempt}"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(source_code)
        log(f"Original backed up to {backup_path}")

        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        log(f"Fix written to {TARGET_FILE}.")

    # ── Final verification after all attempts ─────────────────────────────
    log(f"\n>>> Final verification after {MAX_ATTEMPTS} attempt(s)")
    passed, test_output = run_tests()
    if passed:
        log("All tests PASSED after repair.")
        log("RESULT: SUCCESS")
    else:
        log("Tests still failing after all attempts exhausted.")
        log(f"Final pytest output:\n{test_output}")
        log("RESULT: FAILED — manual intervention required.")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    healing_loop()
