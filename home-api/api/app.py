import os

from flask import Flask
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .schema import schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{user}:{password}@{host}/{db}'.format(
    user=os.getenv('DB_USER', 'admin'),
    password=os.getenv('DB_PASS', 'development'),
    host=os.getenv('DB_HOST', 'pg'),
    db=os.getenv('DB_NAME', 'api_development')
)

db = SQLAlchemy(app)

from .models.transaction import Transaction

migrate = Migrate(app, db)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql',
        schema=schema,
        graphiql=True
    )
)
