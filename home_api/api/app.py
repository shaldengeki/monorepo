from graphql_server.flask import GraphQLView

from home_api.api.config import app
from home_api.api.graphql.schema import Schema

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=Schema(), graphiql=True),
)
