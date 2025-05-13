from flask import Blueprint
from flask import render_template, request, redirect, Response
from flask_login import login_required, current_user

import tools
from database.database import db
from database.db_models import Question, Poll

bp = Blueprint(
    "polls_system_blueprint",
    __name__,
    template_folder="templates"
)


@bp.route("/questions")
@login_required
def questions_list():
    questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()
    return render_template("questions.html", title="Мои вопросы", questions=questions)


@bp.route("/answers/<question_id>")
@login_required
def question_answers(question_id: str):
    question = db.session.query(Question).filter(Question.id == question_id).one_or_none()
    if not question:
        return redirect("/questions")

    return render_template("answers.html", title="Ответы на вопрос", question=question)


@bp.route("/polls")
@login_required
def polls_list():
    polls = db.session.query(Poll).filter(Poll.user_id == current_user.id).all()
    return render_template("polls.html", title="Мои опросы", polls=polls)


@bp.route("/poll-questions/<poll_id>")
@login_required
def poll_questions(poll_id: str):
    poll = db.session.query(Poll).filter(Poll.id == poll_id and Poll.user_id == current_user.id).one_or_none()
    if not poll:
        return redirect("/polls")

    all_questions = db.session.query(Question).filter(Question.user_id == current_user.id).all()
    other_questions = [question for question in all_questions if question not in poll.questions]

    return render_template("poll_questions.html", title="Вопросы для опроса", other_questions=other_questions,
                           poll=poll)


@bp.route("/public/polls/<poll_id>", methods=["POST", "GET"])
def poll_form(poll_id: str):
    form_response = None
    poll = db.session.query(Poll).filter(Poll.id == poll_id).one_or_none()

    if request.method == "POST":
        form_response = tools.handle_poll_form(poll_id)

    if type(form_response) is Response:
        return form_response

    return render_template("poll_form.html", title="Прохождение опроса", poll=poll,
                           error=form_response, public=True)


@bp.route("/public/polls/done")
def poll_form_done():
    return render_template("poll_form_done.html", title="Опрос пройден", public=True)
