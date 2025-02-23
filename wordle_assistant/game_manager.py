import pandas as pd
from typing import List, Tuple, Dict
from wordle_assistant.core import wordle_filter, create_words_df


class WordleUser:
    def __init__(self, username: str):
        self.username = username
        self.guesses: List[str] = []
        self.letter_states: List[Tuple[int, int, int, int, int]] = []
        self.completed = False
        self.word_found = False
        self.word_list_df = create_words_df()  # Each user has their own word list
        self.answer = None 

    def add_guess(self, guess: str, letter_state: Tuple[int, int, int, int, int]):
        """
        Adds a guess and its corresponding letter states.
        """
        self.guesses.append(guess)
        self.letter_states.append(letter_state)
        self.filter_word_list()  # Update their word list after each guess
    
    def filter_word_list(self):
        """
        Updates the possible word list based on the user's guesses and feedback.
        """
        self.word_list_df = wordle_filter(self.word_list_df, user=self)

    def mark_completed(self, word_found: bool):
        """
        Marks the game as completed for the user.
        """
        self.completed = True
        self.word_found = word_found
    

class WordleGame:
    def __init__(self):
        """
        Initializes a new Wordle game where each user has their own answer.
        """
        self.users: Dict[str, WordleUser] = {}
        self.active = True

    def choose_random_answer(self) -> str:
        """
        Selects a random common word from the default word list and returns it.
        """
        word_list_df = create_words_df()
        return word_list_df[word_list_df["rarity"] == "common"].sample(n=1)["word"].values[0]

    def add_user(self, username: str):
        """
        Adds a new user to the game with their own word list and assigns them a random answer.
        """
        if username not in self.users:
            self.users[username] = WordleUser(username)
            self.users[username].answer = self.choose_random_answer()

    def process_guess_feedback(self, username: str, guess: str) -> Tuple[int, int, int, int, int]:
        """
        Processes a user's guess and returns letter states feedback.
        """
        if username not in self.users:
            raise ValueError("User not found in the game.")
        user = self.users[username]
        if not user.answer:
            raise ValueError("No answer has been set for this user.")

        guess = guess.lower()
        letter_state = []
        for i, letter in enumerate(guess):
            if letter == user.answer[i]:
                letter_state.append(1)  # Green (correct position)
            elif letter in user.answer:
                letter_state.append(2)  # Yellow (wrong position)
            else:
                letter_state.append(0)  # Gray (not in word)
        letter_state_tuple = tuple(letter_state)
        
        user.add_guess(guess, letter_state_tuple)
        
        if guess == user.answer:
            user.mark_completed(word_found=True)
        elif len(user.guesses) >= 6:
            user.mark_completed(word_found=False)

        return letter_state_tuple #should append this to a letter_state list for the user
    
    def check_game_status(self) -> bool:
        """
        Checks if all players have completed their games.
        """
        if all(user.completed for user in self.users.values()):
            self.active = False
        return self.active

