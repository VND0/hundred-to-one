import os

from flask import Flask, render_template, request, redirect, abort, Response
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_restful import Api

import tools
from database.database import db
from database.db_models import User, Question, Poll
from polls_resource import PollResource, PollsListResource
from questions_resource import QuestionResource, QuestionListResource

app = Flask(__name__)

app.config["SECRET_KEY"] = "1"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/database/database.db"

app.jinja_env.auto_reload = True
db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "auth"

api = Api(app)

api.add_resource(QuestionResource, "/api/questions/<question_id>")
api.add_resource(QuestionListResource, "/api/questions")

api.add_resource(PollsListResource, "/api/polls")
api.add_resource(PollResource, "/api/polls/<poll_id>")


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).one_or_none()


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/profile")
    return render_template("index.html", title="Welcome")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    form_response = None
    action_type = "registration"

    if current_user.is_authenticated:
        return redirect("/profile")

    if request.method == "POST":
        action = request.form.get("action-type")
        if action == "registration":
            form_response = tools.handle_registration()
        elif action == "login":
            action_type = "login"
            form_response = tools.handle_login()
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
    return redirect("/")


@app.get("/profile")
@login_required
def user_profile():
    return render_template("profile.html", title=f"Профиль {current_user.nickname}")


@app.route("/settings", methods=["POST", "GET"])
@login_required
def user_settings():
    load_tab = "edit_data"
    form_response = None
    if request.method == "POST":
        form = request.form
        action = form.get("action-type")
        if action == "edit_data":
            form_response = tools.handle_edit_data()
        elif action == "new_password":
            load_tab = "new_password"
            form_response = tools.handle_change_password()
        elif action == "remove":
            load_tab = "remove"
            form_response = tools.handle_remove_account()
        else:
            abort(400, "Unknown action")

    if type(form_response) is Response:
        return form_response
    else:
        return render_template("settings.html", title=f"Настройки {current_user.nickname}",
                               action_type=load_tab, error=form_response)


@app.route("/questions")
@login_required
def questions_list():
    questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()
    return render_template("questions.html", title="Мои вопросы", questions=questions)


@app.route("/polls")
@login_required
def polls_list():
    polls = db.session.query(Poll).filter(Poll.user_id == current_user.id).all()
    return render_template("polls.html", title="Мои опросы", polls=polls, len=len)


@app.route("/poll-questions/<poll_id>")
def poll_questions(poll_id: str):
    # Добавил, чтобы была заготовка на будущее
    # poll = db.session.query(Poll).filter(Poll.id == poll_id and Poll.user_id == current_user.id).one_or_none()
    # if not poll:
    #     redirect("/polls")
    questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()
    return render_template("poll_questions.html", title="Вопросы для опроса", questions=questions)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, use_reloader=True)
