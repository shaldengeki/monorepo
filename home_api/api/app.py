from graphql_server.flask import GraphQLView

from home_api.api import models
from home_api.api.config import app, db
from home_api.api.graphql import Schema

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=Schema(models), graphiql=True),
)
