from graphql_server.flask.views import GraphQLView

from ark_nova_stats.api.gql import schema
from ark_nova_stats.config import app

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema.Schema(app), graphiql=True),
)
