"""
auth_routes.py
--------------
Handles Login, Registration, and Logout for ALL roles
(user / staff / admin) using the single "users" table.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config.db_config import get_db_connection

# "auth" blueprint groups all authentication-related routes together
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Common login page for User, Staff, and Admin.
    The role is decided by what's stored in the database for that email,
    NOT by which button the person clicked - this keeps it secure.
    """
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")

        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template("auth/login.html")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Check password (supports hashed passwords created via register())
        if user and check_password_hash(user["password"], password):
            # Save login info in the session (cookie-backed, server-side)
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]

            flash(f"Welcome back, {user['full_name']}!", "success")

            # Redirect based on role
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user["role"] == "staff":
                return redirect(url_for("staff.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        else:
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registration page - ONLY for normal customers (role = 'user').
    Staff and Admin accounts are created by the Admin from the Admin panel,
    not through public self-registration (this is standard practice).
    """
    if request.method == "POST":
        full_name = request.form.get("full_name").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")

        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template("auth/register.html")

        cursor = conn.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()

        if existing:
            flash("An account with this email already exists.", "error")
            cursor.close()
            conn.close()
            return render_template("auth/register.html")

        # Hash the password before storing (never store plain text!)
        hashed_password = generate_password_hash(password)

        cursor.execute(
            """INSERT INTO users (full_name, email, password, phone, address, role)
               VALUES (%s, %s, %s, %s, %s, 'user')""",
            (full_name, email, hashed_password, phone, address)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    """Clears the session and sends the person back to the login page."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
