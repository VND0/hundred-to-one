import datetime
import os
from datetime import timedelta

from flask import Flask, render_template, request, redirect, abort, Response, session
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_restful import Api

import games_bp
import polls_system_bp
import tools
from database.database import db
from database.db_models import User
from resources.answers_resource import AnswersListResource, AnswersResource
from resources.games_resource import GamesResource
from resources.poll_questions_resource import PollQuestionResource
from resources.polls_resource import PollResource, PollsListResource
from resources.questions_resource import QuestionResource, QuestionListResource

app = Flask(__name__)

# You may generate your own with command
# $ openssl rand -hex 32
env_secret_key = os.getenv("SECRET_KEY")
if env_secret_key is None:
    raise LookupError("'SECRET_KEY' variable not found in env")

app.config["SECRET_KEY"] = app.config["JWT_SECRET_KEY"] = env_secret_key
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/database/database.db"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)

app.jinja_env.auto_reload = True
db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "auth"

jwt = JWTManager(app)

api = Api(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=31)

api.add_resource(QuestionResource, "/api/questions/<question_id>")
api.add_resource(QuestionListResource, "/api/questions")

api.add_resource(PollsListResource, "/api/polls")
api.add_resource(PollResource, "/api/polls/<poll_id>")

api.add_resource(PollQuestionResource, "/api/poll-questions/<poll_id>")

api.add_resource(AnswersListResource, "/api/answers")
api.add_resource(AnswersResource, "/api/answers/<answer_id>")

api.add_resource(GamesResource, "/api/games/<game_id>")

app.register_blueprint(games_bp.bp)
app.register_blueprint(polls_system_bp.bp)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).one_or_none()


@app.get("/")
def index():
    if current_user.is_authenticated:
        return redirect("/profile")
    return render_template("index.html", title="Hundred To One")


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
    return render_template("auth.html", title="Авторизация", error=form_response, action_type=action_type)


@app.route("/logout")
@login_required
def logout():
    session.permanent = True

    logout_user()
    response = redirect("/")
    response.set_cookie("jwtToken", expires=0)
    return response


@app.get("/profile")
@login_required
def user_profile():
    return render_template("profile.html", title=f"Профиль {current_user.nickname}")


@app.route("/settings", methods=["POST", "GET"])
@login_required
def user_settings():
    form_response = None
    action_type = "edit_data"

    if request.method == "POST":
        form = request.form
        action = form.get("action-type")
        if action == "edit_data":
            form_response = tools.handle_edit_data()
        elif action == "new_password":
            action_type = "new_password"
            form_response = tools.handle_change_password()
        elif action == "remove":
            action_type = "remove"
            form_response = tools.handle_remove_account()
        else:
            abort(400, "Unknown action")

    if type(form_response) is Response:
        return form_response
    return render_template("settings.html", title=f"Настройки {current_user.nickname}",
                           error=form_response, action_type=action_type)


with app.app_context():
    db.create_all()
os.system("npx @tailwindcss/cli -i ./static/src/input.css -o ./static/dist/output.css")
