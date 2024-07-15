import datetime
from datetime import timezone
from typing import Optional

from flask import abort, redirect, request, session
from graphql_server.flask import GraphQLView  # type: ignore

from ark_nova_stats import models
from ark_nova_stats.api.gql import schema
from ark_nova_stats.config import app, db, verify_fitbit_verification

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema.Schema(app), graphiql=True),
)
