import uuid

from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from ..database import models, database

app = Flask(__name__)
app.config["SECRET_KEY"] = "1"


@app.get("/")
def index():
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

    new_user = models.User(id=str(uuid.uuid4()), username=username, email=email,
                           passwd_hash=generate_password_hash(password))
    session.add(new_user)
    session.commit()
    session.close()

    return redirect("/")


def login_user():
    form = request.form
    session = database.Session()

    email = form.get("email")
    password = form.get("password")

    user = session.query(models.User).filter(models.User.email == email).one_or_none()
    if not user:
        return f"User with {email} doesn't exist", 409
    if not check_password_hash(user.passwd_hash, password):
        return f"Incorrect password", 409

    return redirect("/")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    if request.method == "POST":
        action = request.form.get("action-type")
        if action == "reg":
            return register_user()
        elif action == "login":
            return login_user()
        else:
            return "Unknown action", 400

    return render_template("auth.html")


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    models.Base.metadata.create_all(database.engine)

    app.run(port=8000, host="0.0.0.0", use_reloader=True)
