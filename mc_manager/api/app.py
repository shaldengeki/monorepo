from graphql_server.flask import GraphQLView

from . import models
from .config import app
from .gql import Schema

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=Schema(models),
        context={
            "models": models,
        },
        graphiql=True,
    ),
)

if __name__ == "__main__":
    app.run()
