from flask_login import UserMixin
from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .database import Base

association_table = Table(
    "PQ_connection",
    Base.metadata,
    Column("poll_id", ForeignKey("Poll.id")),
    Column("question_id", ForeignKey("Question.id"))
)


class User(Base, UserMixin):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)

    questions: Mapped[list["Question"]] = relationship(back_populates="user", lazy="joined")
    polls: Mapped[list["Poll"]] = relationship(back_populates="user", lazy="joined")

    def set_password(self, password):
        self.hashed_pwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_pwd, password)


class Question(Base):
    __tablename__ = "Question"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id))

    user: Mapped["User"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "Answer"

    id: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String(50))
    question_id: Mapped[str] = mapped_column(ForeignKey(Question.id))

    question: Mapped["Question"] = relationship(back_populates="answers")


class Poll(Base):
    __tablename__ = "Poll"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    url: Mapped[str]
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id))

    user: Mapped["User"] = relationship(back_populates="polls")
    questions: Mapped[list["Question"]] = relationship(secondary=association_table)
