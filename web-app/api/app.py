import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

from .auth_routes import auth
from .course_routes import courses
from .plan_routes import plans
from .recommendation_routes import recommendations
from .user_routes import user_profile
from api.user_model import create_user, verify_user

# Load .env from the root of the project
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "supersecret"  # needed for session management

# Register blueprints
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(courses, url_prefix="/api/courses")
app.register_blueprint(recommendations, url_prefix="/api/recommendations")
app.register_blueprint(plans, url_prefix="/api/plans")
app.register_blueprint(user_profile, url_prefix="/api/user")


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
    if "user_email" not in session:
        return redirect(url_for("login_page"))
    return render_template("fullplan.html")


@app.route("/editsemester")
def editsemester():
    if "user_email" not in session:
        return redirect(url_for("login_page"))
    return render_template("editsemester.html")
