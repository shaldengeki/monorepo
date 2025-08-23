from graphql_server.flask.views import GraphQLView

from home_api.api.graphql.schema import Schema
from home_api.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=Schema(), graphiql=True),
)
