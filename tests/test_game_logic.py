import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from logic_utils import check_guess, parse_guess, update_score


# --- check_guess ---

def test_winning_guess():
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # Bug fix: guess > secret should be "Too High" (was broken when secret was cast to string)
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # Bug fix: guess < secret should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_check_guess_returns_tuple():
    # check_guess must return (outcome, message), not just a string
    result = check_guess(50, 50)
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_high_low_not_swapped():
    # Regression: verify high/low are not swapped
    outcome_high, _ = check_guess(99, 1)
    outcome_low, _ = check_guess(1, 99)
    assert outcome_high == "Too High"
    assert outcome_low == "Too Low"


# --- update_score: Too High bonus bug ---

def test_too_high_always_deducts_on_even_attempt():
    # Bug fix: even-numbered attempts used to award +5 for "Too High" instead of -5
    score = update_score(100, "Too High", attempt_number=2)
    assert score == 95

def test_too_high_always_deducts_on_odd_attempt():
    score = update_score(100, "Too High", attempt_number=3)
    assert score == 95

def test_too_low_always_deducts():
    score = update_score(100, "Too Low", attempt_number=2)
    assert score == 95

def test_win_awards_points():
    score = update_score(0, "Win", attempt_number=1)
    assert score > 0

def test_win_score_never_below_minimum():
    # Even on a very late attempt, score bonus should not go below 10
    score = update_score(0, "Win", attempt_number=100)
    assert score >= 10


# --- parse_guess ---

def test_parse_guess_valid_integer():
    ok, value, _ = parse_guess("42")
    assert ok is True
    assert value == 42

def test_parse_guess_valid_float_truncates():
    ok, value, _ = parse_guess("7.9")
    assert ok is True
    assert value == 7

def test_parse_guess_empty_string():
    ok, value, _ = parse_guess("")
    assert ok is False
    assert value is None

def test_parse_guess_none():
    ok, value, _ = parse_guess(None)
    assert ok is False
    assert value is None

def test_parse_guess_non_numeric():
    ok, value, _ = parse_guess("abc")
    assert ok is False
    assert value is None
