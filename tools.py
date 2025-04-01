import uuid

from flask import request, Response, redirect
from flask_login import login_user, current_user, logout_user
from pydantic import ValidationError

import models
from database.database import db
from database.db_models import User
from init_account import add_questions
from models import PasswordsUnmatch, UserCreate


def get_errors(e: ValidationError) -> str:
    errors = []
    for error_object in e.errors():
        loc = error_object["loc"][0]
        if "email" in loc:
            errors.append("Допустимая длина почты - от 5 до 100 символов.")
        elif "password" in loc:
            errors.append("В пароле разрешены цифры, латиница и специальные символы. Допустимая длина - от 8 до 60 символов.")
        elif "nickname" in loc:
            errors.append("Допустимая длина никнейма - от 6 до 30 символов.")
        elif "question" in loc:
            errors.append("Допустимая длина вопроса - от 4 до 250 символов.")
        elif "poll" in loc:
            errors.append("Допустимая длина названия опроса - от 2 до 100 символов.")
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

    return redirect("/profile")


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

    return redirect("/profile")


def handle_edit_data() -> str |None:
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


def handle_change_password() -> str | None:
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


def handle_remove_account() -> str | None:
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
