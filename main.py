from flask import Flask, render_template, request, redirect, abort, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pydantic import ValidationError

import models
from database.cruds.user_crud import get_user_by_id, get_user_by_email, create_user
from database.database import create_db_and_tables

app = Flask(__name__)

app.config["SECRET_KEY"] = "1"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/profile")
    return render_template("index.html", title="Welcome")


def handle_registration() -> str | Response:
    form = request.form

    try:
        form_data = models.NewUser(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password"),
            password_confirmation=form.get("password-confirmation"),
        )
    except models.PasswordsUnmatch:
        return "Пароли не совпадают"
    except ValidationError as e:
        what_happened = e.errors()[0]["loc"][0]
        if what_happened == "email":
            return "Некорректная почта"

    new_user = create_user(form_data.nickname, form_data.email, form_data.password)
    if not new_user:
        return f"Пользователь с почтой {form_data.email} уже существует"

    login_user(new_user)

    return redirect("/profile")


def handle_login() -> str | Response:
    form = request.form

    try:
        model = models.User(
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError:
        pass

    user = get_user_by_email(model.email)
    if not user:
        return f"Пользователя с почтой {model.email} не существует"
    if not user.check_password(model.password):
        return f"Неверный пароль"

    login_user(user)

    return redirect("/profile")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    form_response = None
    action_type = "registration"

    if current_user.is_authenticated:
        return redirect("/profile")

    if request.method == "POST":
        action = request.form.get("action-type")
        if action == "registration":
            form_response = handle_registration()
        elif action == "login":
            action_type = "login"
            form_response = handle_login()
        else:
            abort(400, "Unknown action")

    if type(form_response) is Response:
        return form_response
    else:
        return render_template("auth.html", title="Авторизация", error=form_response, action_type=action_type)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/auth")


@app.get("/profile")
@login_required
def user_profile():
    return render_template("profile.html", title=f"Профиль {current_user.nickname}")


@app.get("/settings")
@login_required
def user_settings():
    return render_template("settings.html", title=f"Настройки {current_user.nickname}")


if __name__ == '__main__':
    create_db_and_tables()
    app.run(host="0.0.0.0", port=8080, use_reloader=True)
