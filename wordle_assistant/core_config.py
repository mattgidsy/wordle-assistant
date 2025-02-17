import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Toggle this manually for test mode
TEST_MODE = False  # Change to True when testing

# Variables
WORDLE_COMMON_WORDS = os.path.join(DATA_DIR, "wordle_common_words.csv")
WORDLE_VALID_WORDS = os.path.join(DATA_DIR, "wordle_valid_words.csv")