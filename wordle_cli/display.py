import pandas as pd
from wordle_assistant.core import get_possible_words, get_possible_common, sort_words


def format_possible_common(word_list_df: pd.DataFrame) -> str:
    """
    Formats and returns possible common words for CLI display.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.

    Returns:
      str: A formatted string of possible common words.
    """
    possible_common = get_possible_common(word_list_df)
    return "\n".join(possible_common["word"].tolist())

def display_feedback(letter_state: tuple):
    """
    Displays feedback using colored emojis based on letter states.

    Args:
      letter_state (tuple): Tuple of integers representing letter states (0=Gray, 1=Green, 2=Yellow).
    """
    feedback_display = ''.join(['🟩' if s == 1 else '🟨' if s == 2 else '⬜' for s in letter_state])
    print(f"Feedback: {feedback_display}")

        
def display_sorted_words(word_list_df: pd.DataFrame, max_uncommon: int = 10):
    """
    Automatically filters, sorts, and displays words: common words first (all), then truncated uncommon words.

    Args:
      word_list_df (pd.DataFrame): The word list DataFrame.
      max_uncommon (int): Maximum number of uncommon words to display. Defaults to 10.
    """
    
    # Filter and sort in one step using Pandas
    rarity_order = {"common": 0, "uncommon": 1}
    sorted_df = (
        word_list_df
        .query("eliminated == False")  # Filter eliminated words
        .assign(rarity_order=word_list_df["rarity"].map(rarity_order))  # Map rarity for sorting
        .sort_values(by=["rarity_order", "word"])  # Sort by rarity then alphabetically
        .drop(columns=["rarity_order"])  # Remove temporary column
    )

    # Separate common and uncommon words
    common_words = sorted_df.query("rarity == 'common'")["word"].tolist()
    uncommon_words = sorted_df.query("rarity == 'uncommon'")["word"].tolist()

    print(f"\nPossible words ({len(common_words) + len(uncommon_words)} total):\n")

    # Print all common words
    if common_words:
        print(f"Common words ({len(common_words)} total):")
        print(", ".join(common_words))

    # Print truncated uncommon words
    if uncommon_words:
        print(f"\nUncommon words ({len(uncommon_words)} total, showing up to {max_uncommon}):")
        print(", ".join(uncommon_words[:max_uncommon]) + ("..." if len(uncommon_words) > max_uncommon else ""))



def display_game_result(username: str, user):
    """
    Displays the game result (win/lose) for the user.

    Args:
      username (str): The player's username.
      user: The WordleUser instance.
    """
    if user.word_found:
        print(f"🎉 Congratulations {username}! You guessed the word! 🎉")
    else:
        print(f"❌ Game over. The correct word was: {user.answer}")
