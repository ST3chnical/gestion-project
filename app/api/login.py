import strawberry
from fastapi import HTTPException, status
from app.security.hash import verify_password
from app.security.token import create_access_token
from app.security.validation import get_user_by_email
from app.utils.login_utils import Login, LoginResponse


@strawberry.type
class LoginMutation:
    @strawberry.mutation
    def login(self, login: Login) -> LoginResponse:
        user = get_user_by_email(login.email)
        if not user or not verify_password(login.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        access_token = create_access_token(data={"sub": user.user_id})
        return LoginResponse(success=True, message="Login successfully", token=access_token)
