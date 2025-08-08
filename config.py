from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "../data")
TREATED_FILE = os.getenv("TREATED_FILE", "treated_items.json")
MODEL_PATH = os.getenv("MODEL_PATH")
QUESTION_TREE_PATH = os.getenv("QUESTION_TREE_PATH")
MAX_CHARS = int(os.getenv("MAX_CHARS", 2000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")