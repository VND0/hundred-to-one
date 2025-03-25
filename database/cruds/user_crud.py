import uuid

from flask_login import current_user

from models import EditUser, ChangingPassword
from ..database import session_generator
from ..models import User

sessions = session_generator()


def get_user_by_id(user_id: str) -> User | None:
    session = next(sessions)
    return session.query(User).filter(User.id == user_id).one_or_none()


def get_user_by_email(email: str) -> User | None:
    session = next(sessions)
    return session.query(User).filter(User.email == email).one_or_none()


def create_user(nickname: str, email: str, password: str) -> User | None:
    session = next(sessions)

    existing_user = get_user_by_email(email)
    if existing_user:
        return None

    new_user = User(
        id=str(uuid.uuid4()),
        nickname=nickname,
        email=email
    )
    new_user.set_password(password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def update_user(user_upd: EditUser) -> None:
    session = next(sessions)

    # user = get_user_by_id(current_user.id)
    user = session.query(User).filter(User.id == current_user.id).one()
    user.email = str(user_upd.email)
    user.nickname = user_upd.nickname

    session.commit()


def update_password(new_password: ChangingPassword) -> None:
    session = next(sessions)

    # user = get_user_by_id(current_user.id)
    user = session.query(User).filter(User.id == current_user.id).one()
    user.set_password(new_password.new_password)

    session.commit()


def delete_user() -> None:
    session = next(sessions)

    # user = get_user_by_id(current_user.id)
    user = session.query(User).filter(User.id == current_user.id).one()
    session.delete(user)
    session.commit()
