from pydantic import BaseModel, Field, model_validator, EmailStr
from typing_extensions import Self

PASSWORD = Field(min_length=8, max_length=60, pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")


class PasswordsUnmatch(Exception):
    pass


class User(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = PASSWORD


class UserCreate(User):
    nickname: str = Field(min_length=6, max_length=30)
    password_confirmation: str = PASSWORD

    @model_validator(mode="after")
    def validate_match(self) -> Self:
        if self.password != self.password_confirmation:
            raise PasswordsUnmatch
        return self


class UserUpdate(BaseModel):
    nickname: str = Field(min_length=6, max_length=30)
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = PASSWORD


class PasswordChange(BaseModel):
    old_password: str = PASSWORD
    new_password: str = PASSWORD
    new_confirmation: str = PASSWORD

    @model_validator(mode="after")
    def validate_match(self) -> Self:
        if self.new_password != self.new_confirmation:
            raise PasswordsUnmatch
        return self


class OnlyPassword(BaseModel):
    password: str = PASSWORD


class Question(BaseModel):
    question: str = Field(min_length=4, max_length=250)


class Poll(BaseModel):
    poll: str = Field(min_length=2, max_length=70)


class PollQuestionsEdit(BaseModel):
    to_added: list[str] = Field(alias="toAdded")
    to_other: list[str] = Field(alias="toOther")


class Answer(BaseModel):
    answer: str = Field(min_length=1, max_length=40)


class AnswerCreate(Answer):
    quantity: int = Field(ge=1, le=10)


class Game(BaseModel):
    game: str = Field(min_length=5, max_length=50)


class GameCreate(Game):
    questions_identifiers: list[str] = Field(min_length=7, max_length=7)
