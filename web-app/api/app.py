import os

from dotenv import load_dotenv
from flask import Flask

# Relative import for auth_routes in the same folder
from .auth_routes import auth


# Load .env from the root of the project
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))


app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")
