import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

"""Flask config."""

class Config:
    """Flask configuration variables."""

    FLASK_APP = os.environ.get('FLASK_APP')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    SQLALCHEMY_DATABASE_URI = 'postgresql://' + os.environ.get("DB_USER") + ':' + os.environ.get("DB_PASS") + '@localhost:5432/' + os.environ.get("DB_NAME")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

EVENT_CODE = "2024vagle"
TEAM = "1086"
YEAR = "2024"
REFRESH = 300
FOUL_RATE = 1.065