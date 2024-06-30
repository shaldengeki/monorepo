from graphql_server.flask import GraphQLView

from skeleton import models
from skeleton.api import gql
from skeleton.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=gql.Schema(models, app), graphiql=True
    ),
)
