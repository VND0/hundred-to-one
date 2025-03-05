import uuid

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from werkzeug.security import generate_password_hash

from ..database import models, database

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "auth"

app.config["SECRET_KEY"] = "1"


@login_manager.user_loader
def load_user(user_id):
    session = database.Session()
    return session.query(models.User).filter(models.User.id == user_id).one_or_none()


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/protected")
    return render_template("index.html")


def register_user():
    form = request.form
    session = database.Session()

    email = form.get("email")
    username = form.get("username")
    password = form.get("password")
    existing_user = session.query(models.User).filter(models.User.email == email).one_or_none()
    if existing_user:
        return f"User with {email} already exists.", 409

    new_user = models.User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=generate_password_hash(password)
    )

    session.add(new_user)
    session.commit()
    session.close()

    return redirect("/auth")


def login_user1():
    form = request.form
    session = database.Session()

    email = form.get("email")
    password = form.get("password")

    user = session.query(models.User).filter(models.User.email == email).one_or_none()
    if not user:
        return f"User with {email} doesn't exist", 409
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
            return register_user()
        elif action == "login":
            return login_user1()
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

    models.Base.metadata.create_all(database.engine)

    app.run(port=8000, host="0.0.0.0", use_reloader=True)
