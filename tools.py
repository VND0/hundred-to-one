import uuid

from flask import request, Response, redirect
from flask_login import login_user, current_user, logout_user
from pydantic import ValidationError

import models
from database import database
from database.models import User
from models import PasswordsUnmatch, NewUser

sessions = database.session_generator()


def create_user(user_data: NewUser) -> User | None:
    session = next(sessions)

    existing_user = session.query(User).filter(User.email == user_data.email).one_or_none()
    if existing_user:
        return None

    new_user = User(
        id=str(uuid.uuid4()),
        nickname=user_data.nickname,
        email=user_data.email
    )
    new_user.set_password(user_data.password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def handle_registration() -> str | Response:
    form = request.form

    try:
        model = models.NewUser(
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

    new_user = create_user(model)
    if not new_user:
        return f"Пользователь с почтой {model.email} уже существует"

    login_user(new_user)

    return redirect("/profile")


def handle_login() -> str | Response:
    form = request.form
    session = next(sessions)

    try:
        model = models.User(
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError:
        raise NotImplementedError

    user = session.query(User).filter(User.email == model.email).one_or_none()
    if not user:
        return f"Пользователя с почтой {model.email} не существует"
    if not user.check_password(model.password):
        return f"Неверный пароль"

    login_user(user)

    return redirect("/profile")


def handle_edit_data():
    session = next(sessions)
    form = request.form
    try:
        model = models.EditUser(
            nickname=form.get("nickname"),
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError:
        raise NotImplementedError

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = session.query(User).filter(User.id == current_user.id).one()
    user.email = str(model.email)
    user.nickname = model.nickname

    session.commit()
    return redirect("/settings")


def handle_change_password():
    session = next(sessions)
    form = request.form
    try:
        model = models.ChangingPassword(
            old_password=form.get("old_password"),
            new_password=form.get("new_password"),
            new_confirmation=form.get("new_confirmation")
        )
    except ValidationError:
        raise NotImplementedError
    except PasswordsUnmatch:
        return "Пароли не совпадают"

    if not current_user.check_password(model.old_password):
        return f"Неверный пароль"

    user = session.query(User).filter(User.id == current_user.id).one()
    user.set_password(model.new_password)
    session.commit()

    return redirect("/settings")


def handle_remove_account():
    session = next(sessions)
    form = request.form
    try:
        model = models.OnlyPassword(password=form.get("password"))
    except ValidationError:
        raise NotImplementedError

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    user = session.query(User).filter(User.id == current_user.id).one()
    session.delete(user)
    session.commit()
    logout_user()
    return redirect("/")
