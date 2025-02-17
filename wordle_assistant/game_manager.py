from wordle_assistant.core import wordle_filter
from typing import Dict, Optional, List
import random
import pandas as pd

class WordleUser:
    def __init__(self):
        self.guesses = []
        self.letter_states = []

# ---- Old Implementation ---- 

class User:
    def __init__(self, user_id: str, word_list: pd.DataFrame):
        self.user_id = user_id
        self.games_played = 0
        self.games_won = 0
        self.word_list = word_list
        self.current_game: Optional['GameSession'] = None
    
    def start_game(self, secret_word: str):
        self.current_game = GameSession(self.user_id, secret_word, self.word_list.copy())
        self.games_played += 1
    
    def end_game(self, won: bool):
        if won:
            self.games_won += 1
        self.current_game = None


class GameSession:
    def __init__(self, user_id: str, secret_word: str, df: pd.DataFrame):
        self.user_id = user_id
        self.secret_word = secret_word.lower()
        self.df = df  # Store filtered words instead of copying each time
        self.guesses: List[str] = []
        self.is_active = True
    
    def make_guess(self, guess: str) -> Dict[str, any]:
        if not self.is_active:
            return {"error": "Game is not active."}
        
        self.guesses.append(guess)
        letters_state = self.evaluate_guess(guess)
        self.df = wordle_filter(self.df, guess, letters_state, self.guesses)
        
        return {
            "user_id": self.user_id,
            "guess": guess,
            "feedback": letters_state,
            "remaining_words": self.df.to_dict(orient='records'),
            "status": "won" if guess == self.secret_word else "lost" if len(self.guesses) >= 6 else "ongoing",
            "secret_word": self.secret_word if not self.is_active else None
        }
    
    def evaluate_guess(self, guess: str) -> List[int]:
        return [
            1 if guess[i] == self.secret_word[i] else 2 if guess[i] in self.secret_word else 0
            for i in range(len(guess))
        ]
        
class GameManager:
    def __init__(self, word_list: pd.DataFrame):
        self.word_list = word_list
        self.active_games: Dict[str, User] = {}
    
    def start_new_game(self, user_id: str) -> Dict[str, any]:
        if user_id in self.active_games and self.active_games[user_id].current_game:
            return {"error": "User already has an active game."}
        
        secret_word = random.choice(self.word_list["word"].tolist())
        user = self.active_games.get(user_id, User(user_id, self.word_list))
        user.start_game(secret_word)
        self.active_games[user_id] = user
        
        return {"user_id": user_id, "secret_word": secret_word}
    
    def make_guess(self, user_id: str, guess: str) -> Dict[str, any]:
        user = self.active_games.get(user_id)
        if not user or not user.current_game:
            return {"error": "No active game for user."}
        
        result = user.current_game.make_guess(guess)
        
        if result["status"] in ["won", "lost"]:
            user.end_game(won=(result["status"] == "won"))
        
        return result