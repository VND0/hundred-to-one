from flask import render_template, request, redirect, abort, Response, Blueprint
from flask_login import login_required, current_user

import tools
from database.database import db
from database.db_models import Question, Game

bp = Blueprint(
    "games_blueprint",
    __name__,
    template_folder="templates",
    url_prefix="/games"
)


@bp.route("")
@login_required
def games_list():
    games = db.session.query(Game).filter(Game.user_id == current_user.id).all()
    return render_template("games.html", title="Мои игры", games=games)


@bp.route("/game-add", methods=["POST", "GET"])
@login_required
def game_add():
    form_response = None
    questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()

    if request.method == "POST":
        form_response = tools.handle_game_form()

    if type(form_response) is Response:
        return form_response

    return render_template("game_add_edit.html", title="Создание игры", error=form_response,
                           questions=questions, game=Game())


@bp.route("/game-edit/<game_id>", methods=["POST", "GET"])
@login_required
def game_edit(game_id: str):
    form_response = None
    questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()

    if request.method == "POST":
        form_response = tools.handle_game_edit(game_id)

    if type(form_response) is Response:
        return form_response

    game = db.session.query(Game).filter(Game.id == game_id).one()
    return render_template("game_add_edit.html", title="Изменение игры", error=form_response,
                           questions=questions, game=game)


@bp.route("/game-info/<game_id>")
@login_required
def game_info(game_id: str):
    game = db.session.query(Game).filter(Game.id == game_id).one_or_none()
    if not game:
        return redirect("/games")

    for question in game.questions:
        question.answers.sort(key=lambda a: a.quantity, reverse=True)
        question.answers = question.answers[:6]

    return render_template("game_info.html", title="Отчет по игре", game=game)


@bp.route("/excel-import", methods=["GET", "POST"])
@login_required
def excel_import():
    error = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file.filename:
            abort(400, "No file chosen")

        response = tools.parse_excel_game(file)
        if type(response) is Response:
            return response
        else:
            error = response

    return render_template("excel_import.html", title="Импорт игры", error=error)
