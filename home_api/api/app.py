from graphql_server.flask import GraphQLView  # type: ignore

from home_api.api.graphql.schema import Schema
from home_api.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=Schema(), graphiql=True),
)
