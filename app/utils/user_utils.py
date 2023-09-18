import strawberry
from typing import Optional


@strawberry.type
class User:
    user_id: int
    username: str
    password: str
    email: str
    name: str
    role_id: int


@strawberry.type
class UserResponse:
    success: bool
    message: str


@strawberry.input
class UserInput:
    user_id: Optional[int] = None
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]
    name: Optional[str]
    role_id: Optional[int]


@strawberry.input
class UserInputCreate:
    user_id: Optional[int] = None
    username: str
    password: str
    email: str
    name: str
    role_id: int