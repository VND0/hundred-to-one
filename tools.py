import uuid

import openpyxl
from flask import request, Response, redirect
from flask_jwt_extended import create_access_token
from flask_login import login_user, current_user, logout_user
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

import models
from database.database import db
from database.db_models import User, Question, Poll, Answer, Game
from init_account import add_questions
from models import PasswordsUnmatch, UserCreate, AnswerCreate, GameCreate


def get_errors(e: ValidationError) -> str:
    errors = []
    for error_object in e.errors():
        loc = error_object["loc"][0]
        if "nickname" in loc:
            errors.append("Допустимая длина никнейма - от 6 до 30 символов")
        elif "email" in loc:
            errors.append("Допустимая длина почты - от 5 до 100 символов")
        elif "password" in loc:
            errors.append("В пароле разрешены цифры, латиница и специальные символы. Длина - от 8 до 60 символов")
        elif "poll" in loc:
            errors.append("Допустимая длина названия опроса - от 2 до 70 символов")
        elif "game_question" in loc:
            errors.append("У игры может быть только 7 вопросов")
        elif "question" in loc:
            errors.append("Допустимая длина вопроса - от 4 до 250 символов")
        elif "answer" in loc:
            errors.append("Допустимая длина ответа - от 1 до 40 символов")
        elif "game" in loc:
            errors.append("Допустимая длина названия игры - от 5 до 50 символов")
        else:
            raise NotImplementedError
    return " ".join(errors)


def create_user(user_data: UserCreate) -> User | None:
    existing_user = db.session.query(User).filter(User.email == user_data.email).one_or_none()
    if existing_user:
        return None

    new_user = User(
        id=str(uuid.uuid4()),
        nickname=user_data.nickname,
        email=user_data.email
    )
    new_user.set_password(user_data.password)

    db.session.add(new_user)
    db.session.commit()
    db.session.refresh(new_user)

    return new_user


def handle_registration() -> str | Response:
    form = request.form

    try:
        model = UserCreate(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password"),
            password_confirmation=form.get("password-confirmation"),
        )
    except PasswordsUnmatch:
        return "Пароли не совпадают"
    except ValidationError as e:
        return get_errors(e)

    new_user = create_user(model)
    if not new_user:
        return f"Пользователь с почтой {model.email} уже существует"

    login_user(new_user)
    add_questions(new_user.id)

    access_token = create_access_token(identity=new_user.id)
    response = redirect("/profile")
    response.set_cookie("jwtToken", access_token)
    return response


def handle_login() -> str | Response:
    form = request.form
    try:
        model = models.User(
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError as e:
        return get_errors(e)

    user = db.session.query(User).filter(User.email == model.email).one_or_none()
    if not user:
        return f"Пользователя с почтой {model.email} не существует"
    if not user.check_password(model.password):
        return f"Неверный пароль"

    login_user(user)

    access_token = create_access_token(identity=user.id)
    response = redirect("/profile")
    response.set_cookie("jwtToken", access_token)
    return response


def handle_edit_data() -> str | Response:
    form = request.form
    try:
        model = models.UserUpdate(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError as e:
        return get_errors(e)

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()
    user.email = str(model.email)
    user.nickname = model.nickname

    db.session.commit()
    return redirect("/settings")


def handle_change_password() -> str | Response:
    form = request.form
    try:
        model = models.PasswordChange(
            old_password=form.get("old_password"),
            new_password=form.get("new_password"),
            new_confirmation=form.get("new_confirmation")
        )
    except ValidationError as e:
        return get_errors(e)
    except PasswordsUnmatch:
        return "Новый пароль и его подтверждение не совпадают"

    if not current_user.check_password(model.old_password):
        return f"Неверный текущий пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()
    user.set_password(model.new_password)
    db.session.commit()

    return redirect("/settings")


def handle_remove_account() -> str | Response:
    form = request.form
    try:
        model = models.OnlyPassword(password=form.get("password"))
    except ValidationError as e:
        return get_errors(e)

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()

    for question in user.questions:
        for answer in question.answers:
            db.session.delete(answer)
        db.session.delete(question)

    for poll in user.polls:
        db.session.delete(poll)

    db.session.delete(user)
    db.session.commit()

    logout_user()
    return redirect("/")


def handle_poll_form(poll_id: str) -> str | Response:
    form = request.form

    poll = db.session.query(Poll).filter(Poll.id == poll_id).one()
    for index, question in enumerate(poll.questions):
        create_answer = True
        try:
            model = AnswerCreate(
                answer=form.get(f"answer-{index + 1}")
            )
        except ValidationError as e:
            return get_errors(e)

        for answer in question.answers:
            if answer.answer == model.answer:
                answer.quantity += 1
                create_answer = False

        if create_answer:
            new_answer = Answer(
                id=str(uuid.uuid4()),
                answer=model.answer,
                question_id=question.id,
                quantity=1
            )
            db.session.add(new_answer)
    db.session.commit()

    return redirect("/public/polls/done")


def handle_game_form() -> str | Response:
    form = request.form

    try:
        model = GameCreate(
            game=form.get("game"),
            questions_identifiers=form.getlist("question")
        )
    except ValidationError as e:
        return get_errors(e)

    new_game = Game(
        id=str(uuid.uuid4()),
        game=model.game,
        user_id=current_user.id
    )

    for question_id in model.questions_identifiers:
        question = db.session.query(Question).filter(
            Question.id == question_id and current_user.id == question.user_id).one()
        new_game.questions.append(question)

    try:
        db.session.add(new_game)
        db.session.commit()
    except IntegrityError as e:
        return type(e).__name__

    return redirect("/games")


def handle_game_edit(game_id: str):
    form = request.form
    try:
        model = GameCreate(
            game=form.get("game"),
            questions_identifiers=form.getlist("question")
        )
    except ValidationError as e:
        return get_errors(e)

    game = db.session.query(Game).filter(Game.id == game_id).one()
    game.game = model.game
    game.questions.clear()
    for question_id in model.questions_identifiers:
        question = db.session.query(Question).filter(Question.id == question_id and
                                                     Question.user_id == current_user.id).one()
        game.questions.append(question)

    try:
        db.session.commit()
    except IntegrityError as e:
        return type(e).__name__

    return redirect("/games")


def parse_excel_game(file: FileStorage) -> Response | str:
    wb = openpyxl.load_workbook(filename=file.stream)
    sheet = wb.active

    # Parsing name of the game
    game_index = "B1"
    game = sheet[game_index].value
    try:
        models.Game(game=game)
    except ValidationError as e:
        return get_errors(e)

    # Parsing questions
    question_indexes = ("B4", "B12", "B21", "B29", "B38", "B46", "B55")
    questions = [sheet[index].value for index in question_indexes]
    try:
        for question in questions:
            models.Question(question=question)
    except ValidationError as e:
        return f"{get_errors(e)}. Вопрос: {question}."
    if len(set(questions)) != len(questions):
        return f"Вопросы повторяются."

    # Parsing answers
    answers_indexes = ("B5:B10", "B13:B18", "B22:B27", "B30:B35", "B39:B44", "B47:B52", "B56:B61")
    answers = []
    try:
        for index in answers_indexes:
            answers.append([])
            row = sheet[index]
            for answer in row:
                val = answer[0].value
                models.Answer(answer=val)
                answers[-1].append(val)

            if len(answers[-1]) != len(set(answers[-1])):
                return f"Ответы повторяются."
    except ValidationError as e:
        return f"{get_errors(e)}. Ответ: {val}"

    # Parsing scores
    scores_indexes = ("D5:D10", "D13:D18", "D22:D27", "D30:D35", "D39:D44", "D47:D52")
    scores = []
    try:
        for index in scores_indexes:
            scores.append([])
            row = sheet[index]
            for score in row:
                val = score[0].value
                assert type(val) is int
                assert 1 <= val <= 95
                scores[-1].append(val)
    except AssertionError:
        return f"Одно или несколько очков - не целое число в диапазоне [1;95]"
    scores.append([15, 30, 60, 120, 180, 240])

    add_game_to_db(game, questions, answers, scores)
    return redirect("/games")


def add_game_to_db(game: str, questions: list[str], answers: list[list[str]], scores: list[list[str]]) -> None:
    user_id = current_user.id
    new_game = Game(
        id=str(uuid.uuid4()),
        game=game,
        user_id=user_id
    )
    db.session.add(new_game)

    for index, question in enumerate(questions):
        new_question = Question(
            id=str(uuid.uuid4()),
            question=question,
            user_id=user_id
        )
        new_game.questions.append(new_question)

        new_answers = []
        for answer, score in zip(answers[index], scores[index]):
            new_answer = Answer(
                id=str(uuid.uuid4()),
                answer=answer,
                question_id=new_question.id,
                quantity=score
            )
            new_answers.append(new_answer)
        new_question.answers.extend(new_answers)

    db.session.commit()
