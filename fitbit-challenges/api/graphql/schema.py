from graphql import GraphQLObjectType, GraphQLSchema, GraphQLField, GraphQLString


def get_test_field(*args, **kwargs) -> str:
    return "hello world!"


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="Query",
            fields={
                "test": GraphQLField(
                    GraphQLString,
                    args={},
                    resolve=get_test_field,
                    description="Test field",
                )
            },
        )
    )
