from graphql_server.flask import GraphQLView
from .config import app
from . import models

from . import gql

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=gql.Schema(models), graphiql=True),
)
