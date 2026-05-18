from pydantic import BaseModel, EmailStr, Field


class BaseAuth(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class Login(BaseAuth):
    pass


class Signup(BaseAuth):
    name: str = Field(min_length=3)
