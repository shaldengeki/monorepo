from graphql_server.flask.views import GraphQLView

from skeleton.api.gql import schema
from skeleton.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema.Schema(app), graphiql=True),
)
