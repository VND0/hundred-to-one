from typing import Optional

from pydantic import BaseModel, Field, model_validator, EmailStr
from typing_extensions import Self


class PasswordsUnmatch(Exception):
    pass


class User(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=60,
                          pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")


class NewUser(User):
    nickname: str = Field(min_length=6, max_length=30)
    password_confirmation: str = Field(min_length=8, max_length=60,
                                       pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")

    @model_validator(mode="after")
    def validate_match(self) -> Self:
        if self.password != self.password_confirmation:
            raise ValueError("Passwords don't match")
        return self


class EditUser(BaseModel):
    nickname: Optional[str] = Field(default=None, min_length=6, max_length=30)
    email: Optional[EmailStr] = Field(default=None, min_length=5, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=60,
                                    pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")
    password_confirmation: Optional[str] = Field(default=None, min_length=8, max_length=60,
                                                 pattern=r"""^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$""")

    @model_validator(mode="after")
    def validate_match(self) -> Self:
        if self.password is None and self.password_confirmation is None:
            return self
        if self.password != self.password_confirmation:
            raise PasswordsUnmatch
        return self


class Question(BaseModel):
    name: str = Field(min_length=4, max_length=250)


class Answer(BaseModel):
    value: str = Field(min_length=2, max_length=100)
