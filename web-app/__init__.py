"""
web-app package initializer.
Sets up Flask app, and routes.
"""

import os

from flask import Flask, redirect, url_for, session, render_template


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ----------------------
    # Home Route Fix
    # ----------------------
    @app.route("/")
    def home():
        return render_template("home.html")

    return app
