from flask import Flask, render_template, request, redirect, abort, Response
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


def handle_registration() -> str | Response:
    form = request.form

    email = form.get("email")
    nickname = form.get("nickname")
    password = form.get("password")
    confirmation = form.get("password-confirmation")

    if password != confirmation:
        return f"Passwords don't match"

    new_user = create_user(nickname, email, password)
    if not new_user:
        return f"User with email {email} already exist"

    login_user(new_user)
    return redirect("/auth")


def handle_login() -> str | Response:
    form = request.form

    email = form.get("email")
    password = form.get("password")

    user = get_user_by_email(email)
    if not user:
        return f"User with email {email} doesn't exist"
    if not user.check_password(password):
        return f"Incorrect password"

    login_user(user)

    return redirect("/protected")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    form_resp = None
    action_type = "reg"
    if current_user.is_authenticated:
        return redirect("/protected")
    if request.method == "POST":
        action = request.form.get("action-type")
        if action == "reg":
            form_resp = handle_registration()
        elif action == "login":
            action_type = "login"
            form_resp = handle_login()
        else:
            abort(400, "Unknown action")

    if type(form_resp) is Response:
        return form_resp
    else:
        return render_template("auth.html", title="Авторизация", err=form_resp, action_type=action_type)


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
