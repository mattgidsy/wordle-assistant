from wordle_assistant.core import wordle_filter, load_word_list


def parse_feedback(feedback: str) -> tuple[int, int, int, int, int]:
    """
    Converts user-friendly feedback ('x', '!', '?') into the tuple format (0,1,2).
    Expected input format: A 5-character string containing only 'x', '!', or '?'.
    """
    symbol_map = {'x': 0, '!': 1, '?': 2}
    
    if len(feedback) != 5 or not all(c in symbol_map for c in feedback):
        raise ValueError("Feedback must be a 5-character string containing only 'x', '!', or '?'.")
    
    return tuple(symbol_map[c] for c in feedback)

def interactive_mode():
    """
    Runs an interactive session where the player keeps refining guesses.
    """
    df = load_word_list()  # ✅ Load word list only when needed
    
    print("\n🔠 Welcome to Wordle Assistant!")
    print("Enter your 5-letter guess followed by feedback (e.g., 'slate x!?x?').")
    print("Feedback format:")
    print("  x = Gray (letter is NOT in the word)")
    print("  ! = Green (letter is correct and in the RIGHT position)")
    print("  ? = Yellow (letter is correct but in the WRONG position)")
    print("Type 'quit' to exit at any time.\n")

    while True:
        user_input = input("Enter guess and feedback (or 'quit' to exit): ").strip().lower()

        if user_input == "quit":
            print("👋 Exiting Wordle Assistant. Goodbye!")
            break

        try:
            guess, feedback_str = user_input.split()
            feedback = parse_feedback(feedback_str)
        except ValueError:
            print("❌ Invalid input! Enter in format: <guess> <feedback> (e.g., 'slate x!?x?')")
            continue

        if len(guess) != 5 or not guess.isalpha():
            print("❌ Error: Guess must be a 5-letter word.")
            continue

        # Apply filtering
        df = wordle_filter(df, guess, feedback)

        # Display remaining words
        if df.empty:
            print("⚠️ No words found. Try a different approach!")
        elif len(df) == 1:
            print(f"🎉 The solution is: {df.iloc[0]['word']}! You got it!")
            break
        else:
            print(f"🔎 {len(df)} possible words remaining:")
            print(", ".join(df['word'].head(10)))  # Show only first 10 words for readability
            print("...") if len(df) > 10 else None

if __name__ == "__main__":
    interactive_mode()
