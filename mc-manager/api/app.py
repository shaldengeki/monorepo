from graphql_server.flask import GraphQLView

from .config import app
from . import gql
from . import models

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=gql.Schema(models),
        context={
            "models": models,
        },
        graphiql=True,
    ),
)

if __name__ == "__main__":
    app.run()
