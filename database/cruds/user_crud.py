import uuid

from ..database import Session
from ..models import User


def get_user_by_id(user_id: str) -> User | None:
    session = Session()
    try:
        user = session.query(User).filter(User.id == user_id).one_or_none()
        if user:
            session.expunge(user)
        return user
    finally:
        session.close()


def get_user_by_email(email: str) -> User | None:
    session = Session()
    try:
        return session.query(User).filter(User.email == email).one_or_none()
    finally:
        session.close()


def create_user(username: str, email: str, password: str) -> User | None:
    session = Session()
    try:
        existing_user = get_user_by_email(email)
        if existing_user:
            return None

        new_user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email
        )
        new_user.set_password(password)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user
    finally:
        session.close()


def update_user(email: str, pwd: str, new_name: str = None, new_email: str = None, new_pwd: str = None) -> User | None:
    session = Session()
    try:
        user = get_user_by_email(email)
        if not user:
            return None
        if not user.check_password(pwd):
            return None

        if new_name:
            user.username = new_name
        if new_email:
            user.email = new_email
        if new_pwd:
            user.set_password(new_pwd)
        session.commit()

        return user
    finally:
        session.close()


def delete_user(email: str, pwd: str) -> bool | None:
    session = Session()
    try:
        user = get_user_by_email(email)
        if not user:
            return None
        if not user.check_password(pwd):
            return None

        session.delete(user)
        session.commit()

        return True
    finally:
        session.close()
