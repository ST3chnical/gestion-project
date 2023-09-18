from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str
    password: str
    email: str
    name: str
    rol_id: int
