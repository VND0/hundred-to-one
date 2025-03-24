import uuid

from ..database import session_generator
from ..models import User

sessions = session_generator()


def get_user_by_id(user_id: str) -> User | None:
    session = next(sessions)
    return session.query(User).filter(User.id == user_id).one_or_none()


def get_user_by_email(email: str) -> User | None:
    session = next(sessions)
    return session.query(User).filter(User.email == email).one_or_none()


def create_user(username: str, email: str, password: str) -> User | None:
    session = next(sessions)

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


def update_user(email: str, pwd: str, new_name: str = None, new_email: str = None, new_pwd: str = None) -> User | None:
    session = next(sessions)

    user = get_user_by_email(email)
    if not (user and user.check_password(pwd)):
        return None

    if new_name:
        user.username = new_name
    if new_email:
        user.email = new_email
    if new_pwd:
        user.set_password(new_pwd)
    session.commit()

    return user


def delete_user(email: str, pwd: str) -> bool:
    session = next(sessions)

    user = get_user_by_email(email)
    if not (user and user.check_password(pwd)):
        return False

    session.delete(user)
    session.commit()
    return True
