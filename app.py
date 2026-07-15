from flask import Flask, render_template, redirect, url_for, session
import os
import traceback

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.staff_routes import staff_bp
from routes.admin_routes import admin_bp


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "college_mini_project_secret_key_2026"
)


app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(admin_bp)



@app.route("/health")
def health():
    return "Health OK"



@app.route("/")
def home():

    try:

        if "user_id" in session:

            role = session.get("role")

            if role == "admin":
                return redirect(url_for("admin.dashboard"))

            elif role == "staff":
                return redirect(url_for("staff.dashboard"))

            else:
                return redirect(url_for("user.dashboard"))

        return redirect(url_for("auth.login"))

    except Exception as e:
        traceback.print_exc()
        return str(e), 500



@app.errorhandler(404)
def page_not_found(e):
    return render_template("shared/404.html"), 404



@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return str(e), 500



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )