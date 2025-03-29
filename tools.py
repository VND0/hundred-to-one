import uuid

from flask import request, Response, redirect
from flask_login import login_user, current_user, logout_user
from pydantic import ValidationError

import models
from database.database import db
from database.db_models import User
from models import PasswordsUnmatch, NewUser


def what_happened(e: ValidationError) -> str:
    errors = []
    for err_obj in e.errors():
        loc = err_obj["loc"][0]
        if "email" in loc:
            errors.append("Некорректный адрес почты. Разрешена длина [5;100].")
        elif "passw" in loc:
            errors.append("Некорректный пароль. Разрешены цифры, латиница и специальные символы, длина - [8;60].")
        elif "nickname" in loc:
            errors.append("Разрешенная длина никнейма - [6;30].")
        elif "question" in loc:
            errors.append("Разрешенная длина вопроса - [4; 250]")
        elif "poll" in loc:
            errors.append("Разрешенная длина опроса - [2;100]")
        else:
            raise NotImplementedError
    return " ".join(errors)


def create_user(user_data: NewUser) -> User | None:
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
        model = NewUser(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password"),
            password_confirmation=form.get("password-confirmation"),
        )
    except PasswordsUnmatch:
        return "Пароли не совпадают"
    except ValidationError as e:
        return what_happened(e)

    new_user = create_user(model)
    if not new_user:
        return f"Пользователь с почтой {model.email} уже существует"

    login_user(new_user)

    return redirect("/profile")


def handle_login() -> str | Response:
    form = request.form
    try:
        model = models.User(
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError as e:
        return what_happened(e)

    user = db.session.query(User).filter(User.email == model.email).one_or_none()
    if not user:
        return f"Пользователя с почтой {model.email} не существует"
    if not user.check_password(model.password):
        return f"Неверный пароль"

    login_user(user)

    return redirect("/profile")


def handle_edit_data():
    form = request.form
    try:
        model = models.EditUser(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError as e:
        return what_happened(e)

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()
    user.email = str(model.email)
    user.nickname = model.nickname

    db.session.commit()
    return redirect("/settings")


def handle_change_password():
    form = request.form
    try:
        model = models.ChangingPassword(
            old_password=form.get("old_password"),
            new_password=form.get("new_password"),
            new_confirmation=form.get("new_confirmation")
        )
    except ValidationError as e:
        return what_happened(e)
    except PasswordsUnmatch:
        return "Пароли не совпадают"

    if not current_user.check_password(model.old_password):
        return f"Неверный пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()
    user.set_password(model.new_password)
    db.session.commit()

    return redirect("/settings")


def handle_remove_account():
    form = request.form
    try:
        model = models.OnlyPassword(password=form.get("password"))
    except ValidationError as e:
        return what_happened(e)

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = db.session.query(User).filter(User.id == current_user.id).one()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect("/")
