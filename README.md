# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
A game where you guess a # and are told if the actual # is higher or lower
- [ ] Detail which bugs you found.
The game had several logic bugs in app.py: the attempt counter initialized to 1 instead of 0 (costing players one guess on the first game), the hint message and New Game button hardcoded the range as 1–100 regardless of difficulty, and the Hard difficulty range was set to 1–50 — actually easier than Normal's 1–100. The check_guess function in the original app.py had a broken fallback that compared guesses as strings when secret was cast to a string on even-numbered attempts, which reversed the high/low hints and could produce wrong results. Finally, update_score awarded +5 points for a "Too High" guess on even-numbered attempts instead of always deducting 5, and the game never reset status back to "playing" when starting a new game, so the game would get permanently stuck after a win or loss.
- [ ] Explain what fixes you applied.
The game logic functions (check_guess, parse_guess, update_score) were moved from app.py into logic_utils.py, and several bugs were fixed: the attempt counter was off by one (started at 1 instead of 0), the secret number was sometimes cast to a string which reversed the high/low hints, the Hard difficulty range was easier than Normal (1–50 vs 1–100), the hint message and New Game button ignored the selected difficulty range, and update_score incorrectly awarded +5 points for wrong guesses on even attempts. Pytest tests were also added to tests/test_game_logic.py to verify each of these fixes.

## 📸 Demo

- [ ] [Insert a screenshot of your fixed, winning game here]
![alt text](image.png)

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
