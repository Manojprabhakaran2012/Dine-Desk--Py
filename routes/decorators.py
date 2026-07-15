"""
decorators.py
-------------
Reusable decorators to protect routes based on login state and role.

Usage:
    @login_required(role="staff")
    def some_staff_only_view():
        ...
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(role=None):
    """
    Decorator factory.
    - If role is None: just checks that SOMEONE is logged in.
    - If role is given ("user" / "staff" / "admin"): also checks
      that the logged-in person has that exact role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # 1. Check if logged in at all
            if "user_id" not in session:
                flash("Please log in to continue.", "error")
                return redirect(url_for("auth.login"))

            # 2. Check role match (if a specific role was required)
            if role is not None and session.get("role") != role:
                flash("You are not authorized to view that page.", "error")
                return redirect(url_for("auth.login"))

            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
