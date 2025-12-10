import datetime
import os

import jwt
from flask import Blueprint, jsonify, request, session

from api.user_model import create_user, verify_user

auth = Blueprint("auth", __name__)

SECRET = os.getenv("JWT_SECRET", "defaultsecret")


# -----------------------
#   REGISTER
# -----------------------
@auth.route("/register", methods=["POST"])
def register():
    data = request.json

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400

    new_user = create_user(email, password, name)

    if not new_user:
        return jsonify({"error": "User already exists"}), 400

    # Remove password before sending response
    response_user = new_user.copy()
    response_user.pop("password", None)
    response_user["_id"] = str(response_user["_id"])

    return (
        jsonify({"message": "User registered successfully", "user": response_user}),
        201,
    )


# -----------------------
#   LOGIN
# -----------------------
@auth.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = verify_user(email, password)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT
    token = jwt.encode(
        {
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6),
        },
        SECRET,
        algorithm="HS256",
    )

    # Also set Flask session for web page authentication
    session["user_email"] = user["email"]

    return jsonify({"token": token})
