from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from ..database.database import create_db_and_tables
from ..database.cruds.user_crud import get_user_by_id, get_user_by_email, create_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "1"

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "auth"


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/protected")
    return render_template("index.html")


def check_registration():
    form = request.form

    email = form.get("email")
    username = form.get("username")
    password = form.get("password")

    new_user = create_user(username, email, password)
    if not new_user:
        return f"User with email {email} already exist", 409

    return redirect("/auth")


def check_login():
    form = request.form

    email = form.get("email")
    password = form.get("password")

    user = get_user_by_email(email)
    if not user:
        return f"User with email {email} doesn't exist", 409
    if not user.check_password(password):
        return f"Incorrect password", 409

    login_user(user)

    return redirect("/protected")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    if current_user.is_authenticated:
        return redirect("/protected")
    if request.method == "POST":
        action = request.form.get("action-type")
        if action == "reg":
            return check_registration()
        elif action == "login":
            return check_login()
        else:
            return "Unknown action", 400

    return render_template("auth.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.get("/protected")
@login_required
def protected_route():
    return render_template("protected.html", name=current_user.username)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    create_db_and_tables()

    app.run(port=8000, host="0.0.0.0", use_reloader=True)
