import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Toggle this manually for test mode
TEST_MODE = False  # Change to True when testing

# Variables
COMMON_WORDS = os.path.join(DATA_DIR, "test_words.txt" if TEST_MODE else "common_words.txt")
