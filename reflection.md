# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it? it is a number guessing game where you guess a number from a range of possibilites. The range is based on a difficulty. After each guess you are told if your guess is below or above the actual number.
- List at least two concrete bugs you noticed at the start: The hints were backwards. If you guessed too high it would say too low and vice versa. The new game button did not work meaning you had to refresh to play a new game, and on the first game we had one less guess than we are supposed to have.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? Claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result). The AI suggested I fixed the off by one bug in the very first game. They simply changed the initialization of attempts to 0 instead of 1. I verified this by playing a game and seeing I had the correct number of attempts.
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result). 
The AI suggested I change the hard mode to 1,200. While this logic could be used, I did not instruct it to do this and Hard is harder because we have less guesses. 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed? I either played the game or created a test within pytest
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code. I ran a test to show that we had one less guess than we were supposed to because we started at 1 and not 0 manually.
- Did AI help you design or understand any tests? How? Yes, it was very helpful in writing test cases when giving specific cases to build.
 
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

Why the secret kept changing: Every time you interact with a Streamlit app, clicking a button, typing in a box, Streamlit reruns the entire Python script from top to bottom. In the original app, random.randint() was called unconditionally on every rerun, so a brand new secret was generated on every single interaction, making it impossible to guess.

Streamlit reruns and session state: Imagine Streamlit as a whiteboard that gets completely erased and redrawn every time you click anything. By default, all your variables vanish on each redraw. Session state is like a sticky note you tape to the corner of the whiteboard — it survives the erase. Anything you store in st.session_state persists across reruns so the app can remember things like your score, attempts, and the secret number.

What fixed the stable secret: Wrapping the secret generation in if "secret" not in st.session_state: this check means the secret is only generated once (the very first time the app loads), and every subsequent rerun skips that line because the key already exists in session state.



---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

Writing pytest tests that specifically target each bug before and after fixing it was valuable, having a test that fails first confirms you actually found the bug, and passing after confirms the fix works. 

  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?

I would read all the code carefully before asking the AI to fix anything, so I can give it more specific, targeted prompts instead of broad ones that might change things I didn't intend. 

- In one or two sentences, describe how this project changed the way you think about AI generated code.

I-generated code looks confident and complete but can contain subtle logical bugs that are easy to miss on a quick read.