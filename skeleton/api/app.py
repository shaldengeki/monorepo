import datetime
from datetime import timezone
from typing import Optional

from flask import abort, redirect, request, session
from graphql_server.flask import GraphQLView  # type: ignore

from skeleton import models
from skeleton.api.gql import schema
from skeleton.config import app, db

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema.Schema(app), graphiql=True),
)
