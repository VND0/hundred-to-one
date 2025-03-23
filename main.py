from flask import Flask, render_template, request, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from database.cruds.user_crud import get_user_by_id, get_user_by_email, create_user
from database.database import create_db_and_tables

app = Flask(__name__)
app.config["SECRET_KEY"] = "1"
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/protected")
    return render_template("index.html", title="Hundred To One")


def handle_registration():
    form = request.form

    email = form.get("email")
    nickname = form.get("nickname")
    password = form.get("password")

    new_user = create_user(nickname, email, password)
    if not new_user:
        return f"User with email {email} already exist", 409

    return redirect("/auth")


def handle_login():
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
            return handle_registration()
        elif action == "login":
            return handle_login()
        else:
            abort(400, "Unknown action")

    return render_template("auth.html", title="Авторизация")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.get("/protected")
@login_required
def protected_route():
    return render_template("protected.html", name=current_user.username, title="Вы авторизованы")


if __name__ == '__main__':
    create_db_and_tables()
    app.run(port=8000, host="0.0.0.0", use_reloader=True)
