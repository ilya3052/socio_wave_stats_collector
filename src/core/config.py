import os

from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROTECTED_KEY = os.getenv("PROTECTED_KEY")
APP_ID = os.getenv("APP_ID")

BATCH_SIZE = 100