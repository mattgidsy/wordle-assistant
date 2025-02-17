from wordle_assistant.core import create_word_df
from wordle_assistant.game_manager import GameManager

def get_valid_guess():
    """Prompt the user for a valid 5-letter word guess."""
    while True:
        guess = input("Enter your 5-letter guess: ").strip().lower()
        if len(guess) == 5 and guess.isalpha():
            return guess
        print("Invalid guess. Please enter a 5-letter word.")

def handle_game_response(response):
    """Print feedback and return whether the game should continue."""
    if "error" in response:
        print(response["error"])
        return False

    print("Feedback:", response["feedback"])
    
    remaining_words = [word_data["word"] for word_data in response["remaining_words"]]
    print(f"Remaining possible words ({len(remaining_words)}): {', '.join(remaining_words)}")
    
    if response["status"] == "won":
        print("Congratulations! You guessed the word!")
        return False
    elif response["status"] == "lost":
        print(f"Game over! The word was {response['secret_word']}")
        return False

    return True

def main():
    word_list = create_word_df()
    game_manager = GameManager(word_list)
    
    print("Welcome to Wordle!")
    user_id = input("Enter your unique user ID: ").strip()
    
    start_response = game_manager.start_new_game(user_id)
    if "error" in start_response:
        print(start_response["error"])
        return
    
    print("A new game has started! Try to guess the 5-letter word.")

    while True:
        guess = get_valid_guess()
        response = game_manager.make_guess(user_id, guess)
        if not handle_game_response(response):
            break

    print("Thanks for playing!")

if __name__ == "__main__":
    main()
