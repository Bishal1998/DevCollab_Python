from pydantic import BaseModel, EmailStr, Field


class BaseAuth(BaseModel):
    email: EmailStr
    password: str


class Login(BaseAuth):
    pass


class Signup(BaseAuth):
    name: str = Field(min_length=3)
