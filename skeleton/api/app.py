from graphql_server.flask import GraphQLView  # type: ignore

from skeleton.api.gql import schema
from skeleton.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema.Schema(app), graphiql=True),
)
