# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = f'{BASE_DIR}/app/storage/'
SECRET_KEY = 'secret-key'
