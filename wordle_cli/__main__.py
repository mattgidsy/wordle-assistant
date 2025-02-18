import pandas as pd
import argparse
from wordle_assistant.game_manager import WordleGame

def main():
    parser = argparse.ArgumentParser(description="Wordle Assistant CLI")
    parser.add_argument("--mode", type=str, choices=["game", "test", "blind"], required=True, help="Select mode: game, test, or blind.")
    args = parser.parse_args()
    
    game = WordleGame()
    username = input("Enter your username: ")
    game.add_user(username)

    if args.mode == "game":
        print("Game mode: A random common word has been assigned.")
    elif args.mode == "test":
        answer = input("Enter the correct Wordle answer for this game: ").strip().lower()
        game.users[username].answer = answer
    else:
        print("Blind mode: You will manually enter feedback.")

    while game.active and not game.users[username].completed:
        guess = input("Enter your guess: ").strip().lower()
        if len(guess) != 5:
            print("Invalid guess. Please enter a 5-letter word.")
            continue
        
        if args.mode == "blind":
            feedback = input("Enter feedback (0 = Gray, 1 = Green, 2 = Yellow, exactly 5 numbers): ")
            if len(feedback) != 5 or not feedback.isdigit():
                print("Invalid feedback. Please enter exactly 5 numbers (0, 1, or 2).")
                continue
            letter_state = tuple(map(int, feedback))
            game.users[username].add_guess(guess, letter_state)
        else:
            letter_state = game.process_guess_feedback(username, guess)

        feedback_display = ''.join(['🟩' if s == 1 else '🟨' if s == 2 else '⬜' for s in letter_state])
        print(f"Feedback: {feedback_display}")

        # Get remaining words -- Will put in game_manager as  get_possible_words() and will make another called get_common_possible()
        remaining_words_df = game.users[username].word_list_df[game.users[username].word_list_df["eliminated"] == False]
        remaining_words_list = remaining_words_df["word"].tolist()

        # Display up to 10 remaining words -- will make display function here
        if remaining_words_list:
            print(f"Remaining possible words ({len(remaining_words_list)} total): {', '.join(remaining_words_list[:10])}...")
        else:
            print("No possible words left!")

        if game.users[username].completed:
            if game.users[username].word_found:
                print(f"Congratulations {username}! You guessed the word!")
            else:
                print(f"Game over. The correct word was: {game.users[username].answer}")
    
    game.check_game_status()

if __name__ == "__main__":
    main()