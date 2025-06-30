from graphql_server.flask import GraphQLView  # type: ignore

from mc_manager.api import models
from mc_manager.api.gql.schema import Schema
from mc_manager.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=Schema(),
        context={
            "models": models,
        },
        graphiql=True,
    ),
)

if __name__ == "__main__":
    app.run()
