# Statement for enabling the development environment
DEBUG = False

# Define the application directory
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "tmp/storage/"

SECRET_KEY = "secret-key"
