from pydantic import BaseModel, Field, model_validator, EmailStr
from typing_extensions import Self

PASSWORD = Field(min_length=8, max_length=60, pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")


class PasswordsUnmatch(Exception):
    pass


class User(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = PASSWORD


class NewUser(User):
    nickname: str = Field(min_length=6, max_length=30)
    password_confirmation: str = PASSWORD

    @model_validator(mode="after")
    def validate_match(self) -> Self:
        if self.password != self.password_confirmation:
            raise PasswordsUnmatch
        return self


class EditUser(BaseModel):
    nickname: str = Field(min_length=6, max_length=30)
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = PASSWORD


class ChangingPassword(BaseModel):
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


class NewQuestion(Question):
    user_id: str = Field(alias="userId")


class Answer(BaseModel):
    value: str = Field(min_length=2, max_length=100)
