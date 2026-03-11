def update_score(current_score: int, outcome: str, attempt_number: int): #FIX: Refactored logic into logic_utils.py using Copilot Agent mode).
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score 


def parse_guess(raw: str): #FIX: Refactored logic into logic_utils.py using Copilot Agent mode).
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int): #FIX: Refactored logic into logic_utils.py using Copilot Agent mode).
    if guess == secret:
        return "Win", "Correct! You guessed it!"
    elif guess > secret:
        return "Too High", "Too high! Try a lower number."
    else:
        return "Too Low", "Too low! Try a higher number."
