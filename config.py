import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
RUST_ROVER_REGISTRATION_URL = os.getenv("RUST_ROVER_REGISTRATION_URL")
