from flask import Flask
from dotenv import load_dotenv
import os

# Load .env from the root of the project
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Relative import for auth_routes in the same folder
from .auth_routes import auth

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)
