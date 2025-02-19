from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# TODO: add length and regex constraints
association_table = Table(
    "PQ_connection",
    Base.metadata,
    Column("poll_id", ForeignKey("Poll.id")),
    Column("question_id", ForeignKey("Question.id"))
)


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    passwd_hash: Mapped[str]

    questions: Mapped[list["Question"]] = relationship(back_populates="user")
    polls: Mapped[list["Poll"]] = relationship(back_populates="user")


class Question(Base):
    __tablename__ = "Question"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id))

    user: Mapped["User"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "Answer"

    id: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
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
