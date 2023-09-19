import strawberry


@strawberry.input
class Login:
    email: str
    password: str


@strawberry.type
class LoginResponse:
    success: bool
    message: str
    token: str
