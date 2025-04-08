from flask_login import UserMixin
from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .database import db

poll_question = Table(
    "poll-question",
    db.Model.metadata,
    Column("poll_id", ForeignKey("polls.id")),
    Column("question_id", ForeignKey("questions.id"))
)


game_question = Table(
    "game-question",
    db.Model.metadata,
    Column("game_id", ForeignKey("games.id")),
    Column("question_id", ForeignKey("questions.id"))
)


class User(db.Model, SerializerMixin, UserMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)

    questions: Mapped[list["Question"]] = relationship(
        argument="Question",
        back_populates="user"
    )

    polls: Mapped[list["Poll"]] = relationship(
        argument="Poll",
        back_populates="user"
    )

    games: Mapped[list["Game"]] = relationship(
        argument="Game",
        back_populates="user"
    )

    def set_password(self, password):
        self.hashed_pwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_pwd, password)


class Question(db.Model, SerializerMixin):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id), nullable=False)

    user: Mapped["User"] = relationship(
        argument="User",
        back_populates="questions"
    )

    answers: Mapped[list["Answer"]] = relationship(
        argument="Answer",
        back_populates="question"
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "question", name="uq_user_question"),
    )


class Answer(db.Model, SerializerMixin):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(primary_key=True)
    answer: Mapped[str] = mapped_column(String(40), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey(Question.id), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    question: Mapped["Question"] = relationship(
        argument="Question",
        back_populates="answers"
    )

    __table_args__ = (
        db.UniqueConstraint("question_id", "answer", name="uq_question_answer"),
    )


class Poll(db.Model, SerializerMixin):
    __tablename__ = "polls"

    id: Mapped[str] = mapped_column(primary_key=True)
    poll: Mapped[str] = mapped_column(String(70), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id), nullable=False)

    user: Mapped["User"] = relationship(
        argument="User",
        back_populates="polls"
    )

    questions: Mapped[list["Question"]] = relationship(
        secondary=poll_question
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "poll", name="uq_user_poll"),
    )


class Game(db.Model, SerializerMixin):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(primary_key=True)
    game: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id), nullable=False)

    user: Mapped["User"] = relationship(
        argument="User",
        back_populates="games"
    )

    questions: Mapped[list["Question"]] = relationship(
        secondary=game_question
    )
