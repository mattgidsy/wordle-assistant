import argparse
from wordle_assistant.core import get_word_rank
from wordle_assistant.game_manager import WordleGame
from wordle_cli.display import display_feedback, display_game_result, display_ranked_words, command_prompt

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
          print("Legend: | 0 = ⬜ Gray | 1 = 🟩 Green | 2 = 🟨 Yellow | ")
          feedback = input("Enter feedback (5 numbers): ")
          if len(feedback) != 5 or not feedback.isdigit():
              print("Invalid feedback. Please enter exactly 5 numbers (0, 1, or 2).")
              continue
          letter_state = tuple(map(int, feedback))
      else:
          letter_state = game.process_guess_feedback(username, guess)

     # !! Need to trace letter state & create add_letter_state(): to use users[username].add_letter_state() 
      display_feedback(letter_state) # Display feedback (colors)
      game.users[username].add_guess(guess, letter_state) # Step 1: Add the guess (which auto-filters the word list)
      game.users[username].word_list_df = get_word_rank(game.users[username].word_list_df) # Step 2: Rank only the remaining valid words
      display_ranked_words(game.users[username].word_list_df) # Display ranked words based on updated rankings
      
      # Handle post-guess commands
      if not command_prompt(game, username):
          break  # Exit the game if the user chooses to quit

      # Check if game is completed
      if game.users[username].completed:
          display_game_result(username, game.users[username])
        
      game.check_game_status()

if __name__ == "__main__":
    main()
