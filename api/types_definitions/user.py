# define your pydantic models here for request and response.
from pydantic import BaseModel,  EmailStr
from typing import List


class LogoutSuccess(BaseModel):
    inactive: bool
    token: str


class AuthToken(BaseModel):
    token: str


class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class CreateUserObject(UserCredentials):
    role: str


class PublicUser(BaseModel):
    id: int
    email: str
    role: str



# example of list with no root properties
# class ListSchema(RootModel):
#     root: List[SampleSchema]
