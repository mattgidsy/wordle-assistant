import pandas as pd
from typing import *
from wordle_assistant import core_config as config 


def create_words_df():
    """
    Loads and merges two word lists into a single Pandas DataFrame with metadata.
    
    Dataframe Schema:
    [index][word][rarity][valid][eliminated][rank][letter_freq]
    """
    try:
        # Load common words and mark them as "common"
        common_words_df = pd.read_csv(
            config.WORDLE_COMMON_WORDS, 
            header=None, 
            names=["word"], 
            dtype=str,  # Ensures all words are treated as strings
            keep_default_na=False  # Prevents automatic conversion of certain words like "FALSE" to NaN
        )
        common_words_df["word"] = common_words_df["word"].str.strip().str.lower()  # Normalize text
        common_words_df["rarity"] = "common"
        
        # Load valid words and mark them as "uncommon" initially
        valid_words_df = pd.read_csv(
            config.WORDLE_VALID_WORDS, 
            header=None, 
            names=["word"], 
            dtype=str,  # Ensures all words are treated as strings
            keep_default_na=False  # Prevents automatic conversion of "FALSE", "TRUE", etc.
        )
        valid_words_df["word"] = valid_words_df["word"].str.strip().str.lower()  # Normalize text
        valid_words_df["rarity"] = "uncommon"

        
        # Merge the DataFrames, ensuring "common" is prioritized for duplicates
        merged_df = pd.concat([common_words_df, valid_words_df]).drop_duplicates(subset=["word"], keep="first")
        
        # Add additional metadata columns
        merged_df["valid"] = True  # Mark all words as valid
        merged_df["eliminated"] = False # Placeholder for filtering
        merged_df["rank"] = None  # Placeholder for ranking
        merged_df["letter_freq"] = None  # Placeholder for letter frequency
        
        
        # Sort alphabetically by word
        merged_df = merged_df.sort_values(by="word").reset_index(drop=True)
        
        # Explicitly add an index column
        merged_df.insert(0, "index", merged_df.index)
        
        return merged_df
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return pd.DataFrame(columns=["index", "word", "rarity", "valid", "eliminated", "rank", "letter_freq"])
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame(columns=["index", "word", "rarity", "valid", "eliminated", "rank", "letter_freq"])

def wordle_filter(
    word_list_df: pd.DataFrame, 
    guesses: List[str] = None, 
    letter_states: List[Tuple[int, int, int, int, int]] = None, 
    user = None 
) -> pd.DataFrame:
    """
    Filters the word list based on either a WordleUser instance or separate guess/letter state inputs.

    Args: 
      :param word_list_df: DataFrame containing possible words.
      :param guesses: List of guessed words (optional if passing a user instance).
      :param letter_states: Corresponding letter states for each guess (optional if passing a user instance).
        0 = Gray - Letter must NOT be in the word at all
        1 = Green - Letter must be in the exact position
        2 = Yellow - Letter must be present but in a different position
      :param user: Optional WordleUser instance to use instead of separate inputs.
      
    Returns:
     filtered_df: A DataFrame with updated 'eliminated' column instead of removing words.
    """
    # Ensure user does not modify parameters in place
    if user:
        from wordle_assistant.game_manager import WordleUser
        guesses = list(user.guesses) if user.guesses else []
        letter_states = list(user.letter_states) if user.letter_states else []

    if not guesses or not letter_states:
        return word_list_df  # No filtering needed if no guesses made

    filtered_df = word_list_df.copy()

    for guess, letter_state in zip(guesses, letter_states):
        for i, (letter, state) in enumerate(zip(guess, letter_state)):
            if state == 1:  # Green - Letter must be in the exact position
                filtered_df.loc[filtered_df["word"].str[i] != letter, "eliminated"] = True
            elif state == 2:  # Yellow - Letter must be present but in a different position
                filtered_df.loc[~filtered_df["word"].str.contains(letter) | (filtered_df["word"].str[i] == letter), "eliminated"] = True
            elif state == 0:  # Gray - Letter must NOT be in the word at all
                filtered_df.loc[filtered_df["word"].str.contains(letter), "eliminated"] = True

    return filtered_df


def get_possible_words(word_list_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame of words that have not been eliminated.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.

    Returns:
      pd.DataFrame: A filtered DataFrame of possible words.
    """
    return word_list_df[word_list_df["eliminated"] == False]


def get_possible_common(word_list_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame of common words that have not been eliminated.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.

    Returns:
      pd.DataFrame: A filtered DataFrame of possible common words.
    """
    return word_list_df[(word_list_df["eliminated"] == False) & (word_list_df["rarity"] == "common")]

def sort_words(word_list_df: pd.DataFrame, by: str = "alphabetical", ascending: bool = True) -> pd.DataFrame:
    """
    Sorts the word list DataFrame based on a given criterion.

    Args:
      word_list_df (pd.DataFrame): The DataFrame containing the word list.
      by (str): Sorting criterion. Options: "alphabetical", "rarity".
      ascending (bool): Whether to sort in ascending order. Defaults to True.

    Returns:
      pd.DataFrame: The sorted DataFrame.
    """
    if by == "alphabetical":
        return word_list_df.sort_values(by="word", ascending=ascending).reset_index(drop=True)
    elif by == "rarity":
        # Sorting rarity: common first, then uncommon, then alphabetically
        rarity_order = {"common": 0, "uncommon": 1}
        
        # Use `.assign()` to avoid modifying a slice and ensure it's a copy
        sorted_df = word_list_df.assign(
            rarity_order=word_list_df["rarity"].map(rarity_order)
        ).sort_values(by=["rarity_order", "word"], ascending=[True, ascending]).drop(columns=["rarity_order"]).reset_index(drop=True)
        
        return sorted_df
    else:
        print(f"Warning: Invalid sorting criteria '{by}', defaulting to alphabetical.")
        return word_list_df.sort_values(by="word", ascending=ascending).reset_index(drop=True)

def get_letter_frequency(word_list_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates letter frequency across the dataset and assigns a letter frequency score to each word.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.

    Returns:
      pd.DataFrame: The updated DataFrame with letter frequency scores in 'letter_freq' column.
    """
    if word_list_df.empty:
        return word_list_df

    # Count letter occurrences across all words
    all_letters = "".join(word_list_df["word"])
    letter_counts = Counter(all_letters)

    # Normalize frequencies
    total_letters = sum(letter_counts.values())
    letter_freq_map = {letter: count / total_letters for letter, count in letter_counts.items()}

    # Assign letter frequency score to each word (sum of unique letter frequencies)
    word_list_df["letter_freq"] = word_list_df["word"].apply(
        lambda word: sum(letter_freq_map[letter] for letter in set(word))  # Only count unique letters per word
    )

    return word_list_df

def get_word_rank(word_list_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates word ranking based on letter frequency and prioritizes common words.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.

    Returns:
      pd.DataFrame: The updated DataFrame with word rankings.
    """
    if word_list_df.empty:
        return word_list_df

    # Split into common and uncommon words
    common_words_df = word_list_df[word_list_df["rarity"] == "common"].copy()
    uncommon_words_df = word_list_df[word_list_df["rarity"] == "uncommon"].copy()

    # Apply letter frequency calculation separately
    common_words_df = get_letter_frequency(common_words_df)
    uncommon_words_df = get_letter_frequency(uncommon_words_df)

    # Boost all common words' rank to ensure they are always ranked higher
    common_words_df["rank"] = common_words_df["letter_freq"] + 1  # Adding 1 as a boost
    uncommon_words_df["rank"] = uncommon_words_df["letter_freq"]  # No boost for uncommon words

    # Combine back into one DataFrame
    ranked_df = pd.concat([common_words_df, uncommon_words_df]).reset_index(drop=True)

    # Sort with common words always first, then by rank
    ranked_df = ranked_df.sort_values(by=["rank", "rarity"], ascending=[False, True])

    return ranked_df