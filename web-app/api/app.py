import os

from dotenv import load_dotenv
from flask import Flask, render_template

from .auth_routes import auth
from .recommendation_routes import recommendations

# Load .env from the root of the project
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(recommendations, url_prefix="/api/recommendations")

from flask import Flask, render_template, request, redirect, url_for, session
from api.user_model import create_user, verify_user

app.secret_key = "supersecret"  # needed for session management


@app.route("/", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = verify_user(email, password)
        if user:
            session["user_email"] = user["email"]
            return redirect(url_for("home"))
        else:
            error = "Invalid email or password"
    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup_page():  # this was register, now Sign In page
    error = None
    success = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if not name or not email or not password:
            error = "Please fill in all fields"
        else:
            new_user = create_user(email, password, name)
            if not new_user:
                error = "User already exists"
            else:
                success = "Sign In successful! Please login."
    return render_template("signup.html", error=error, success=success)


@app.route("/home")
def home():
    if "user_email" not in session:
        return redirect(url_for("login_page"))
    return render_template("home.html", email=session["user_email"])


@app.route("/fullplan")
def fullplan():
    return render_template("fullplan.html")


@app.route("/editsemester")
def editsemester():
    return render_template("editsemester.html")
