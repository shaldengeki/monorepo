from graphql import GraphQLObjectType, GraphQLSchema

from skeleton.api.gql.types.example_model import example_model_field


def Schema(models, app):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "example_model": example_model_field(models.ExampleModel),
            },
        ),
    )
