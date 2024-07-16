from graphql import GraphQLObjectType, GraphQLSchema

from skeleton.api.gql.types.example_model import example_model_field
from skeleton.models import ExampleModel


def Schema(app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "testModel": example_model_field(ExampleModel),
            },
        ),
    )
