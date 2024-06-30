from graphql_server.flask import GraphQLView

from mc_manager.api import models
from mc_manager.api.config import app
from mc_manager.api.gql.schema import Schema

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
