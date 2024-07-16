from graphql import GraphQLObjectType, GraphQLSchema

from ark_nova_stats.api.gql.types.example_model import example_model_field
from ark_nova_stats.models import ExampleModel


def Schema(app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "testModel": example_model_field(ExampleModel),
            },
        ),
    )
