from flask import request, Response, redirect
from flask_login import login_user, current_user
from pydantic import ValidationError

import models
from database.cruds.user_crud import get_user_by_email, create_user, update_user, update_password, delete_user
from models import PasswordsUnmatch


def handle_registration() -> str | Response:
    form = request.form

    try:
        form_data = models.NewUser(
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

    new_user = create_user(form_data.nickname, form_data.email, form_data.password)
    if not new_user:
        return f"Пользователь с почтой {form_data.email} уже существует"

    login_user(new_user)

    return redirect("/profile")


def handle_login() -> str | Response:
    form = request.form

    try:
        model = models.User(
            email=form.get("email"),
            password=form.get("password")
        )
    except ValidationError:
        raise NotImplementedError

    user = get_user_by_email(model.email)
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
    except ValidationError:
        raise NotImplementedError

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    update_user(model)
    return redirect("/settings")


def handle_change_password():
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

    update_password(model)
    return redirect("/settings")


def handle_remove_account():
    form = request.form
    try:
        model = models.OnlyPassword(
            password=form.get("password")
        )
    except ValidationError:
        raise NotImplementedError

    if not current_user.check_password(model.password):
        return f"Неверный пароль"

    delete_user()
    return redirect("/")
