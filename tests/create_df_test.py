from wordle_assistant.core import *

def test_create_word_df():
    """
    Test function to load the word DataFrame and display it.
    """
    df = create_word_df()
    
    if df.empty:
        print("Error: DataFrame is empty. Check file paths and content.")
    else:
        print(df.head(100).to_string(index=False))  # Display first x rows for verification, non-truncated

# Run the test
test_create_word_df()