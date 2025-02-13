import pandas as pd
from wordle_assistant import core_config as config 



def load_word_list():
    """
    Loads the word list from a file and returns it as a Pandas DataFrame.
    """
    with open(config.COMMON_WORDS) as wordle_list:
        lines = wordle_list.readlines()
        word_list = [word.strip() for word in lines]

    return pd.DataFrame({"word": word_list})

def wordle_filter(df: pd.DataFrame, guess: str, letters_state: tuple[int, int, int, int, int]) -> pd.DataFrame:
    """
    Filters a word list based on Wordle-style feedback.
    Args:
        df (pd.DataFrame): A DataFrame containing words as a column named 'word'.
        guess (str): The guessed word (must be 5 letters).
        letters_state (tuple[int, int, int, int, int]): A tuple representing the state of each letter in the guess:
            - 0 = Gray (Letter is incorrect)
            - 1 = Green (Letter is correct and in the right position)
            - 2 = Yellow (Letter is correct but in the wrong position)

    Returns:
        pd.DataFrame: A filtered DataFrame containing words that match the given constraints.
    """
    guess_letters = list(guess.lower())
    
    # Step 1: Identify truly incorrect letters (0 - Gray)
    incorrect_letters = set()
    for i, state in enumerate(letters_state):
        if state == 0:
            if guess_letters[i] not in [guess_letters[j] for j in range(len(guess_letters)) if letters_state[j] in (1, 2)]:
                incorrect_letters.add(guess_letters[i])
    df = df[~df["word"].apply(lambda word: any(letter in word for letter in incorrect_letters))]

    # Step 2: Keep words with correct letters in the right positions (1 - Green)
    for i, state in enumerate(letters_state):
        if state == 1:
            df = df[df["word"].str[i] == guess_letters[i]]

    # Step 3: Ensure misplaced letters exist but are not in the same position (2 - Yellow)
    for i, state in enumerate(letters_state):
        if state == 2:
            df = df[df["word"].str.contains(guess_letters[i])]  # Letter must exist somewhere
            df = df[df["word"].str[i] != guess_letters[i]]  # But not in the same position
    return df



