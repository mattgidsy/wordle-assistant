import pandas as pd
import settings

# Sample word list
with open(settings.COMMON_WORDS) as wordle_list:
    lines = wordle_list.readlines()
    word_list = [word.strip() for word in lines]

df = pd.DataFrame({"word": word_list})

def wordle_filter(df, guess, letters_state):
    guess_letters = list(guess.lower())

    print("\n🔹 Original Word List:")
    print(df)

    # Step 1: Identify truly incorrect letters (Gray ⬜)
    incorrect_letters = set()
    for i, state in enumerate(letters_state):
        if state == 0:
            # If the letter appears elsewhere as 🟨 or 🟩, it's not truly incorrect
            if guess_letters[i] not in [guess_letters[j] for j in range(len(guess_letters)) if letters_state[j] in (1, 2)]:
                incorrect_letters.add(guess_letters[i])

    print("\n🔹 Gray (0) Letters to Remove:", incorrect_letters)

    # Remove words that contain incorrect letters
    df = df[~df["word"].apply(lambda word: any(letter in word for letter in incorrect_letters))]

    print("\n🔹 After Removing Gray (0) Letters:")
    print(df)

    # Step 2: Keep words with correct letters in the right positions (1 - Green)
    for i, state in enumerate(letters_state):
        if state == 1:
            df = df[df["word"].str[i] == guess_letters[i]]

    print("\n🔹 After Keeping Green (1) Letters:")
    print(df)

    # Step 3: Ensure misplaced letters exist but are not in the same position (2 - Yellow)
    for i, state in enumerate(letters_state):
        if state == 2:
            df = df[df["word"].str.contains(guess_letters[i])]  # Letter must exist somewhere
            df = df[df["word"].str[i] != guess_letters[i]]  # But not in the same position

    print("\n🔹 After Filtering for Yellow (2) Letters:")
    print(df)

    return df

# Example test case
filtered_df = wordle_filter(df, "slate", (0,2,1,0,2))
