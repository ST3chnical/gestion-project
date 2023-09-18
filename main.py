import uvicorn
import strawberry

from fastapi import FastAPI
from strawberry.asgi import GraphQL

from app.db.config import config_database
from app.api.user import UserMutation, UserQuery
from app.api.login import LoginMutation


@strawberry.type
class Mutation(UserMutation, LoginMutation):
    ...


@strawberry.type
class Query(UserQuery):
    ...


app = FastAPI()

schema = strawberry.Schema(
    mutation=Mutation,
    query=Query
)


graphql_app = GraphQL(schema)

app.add_route('/graphql', graphql_app)


if __name__ == "__main__":
    config_database()
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
