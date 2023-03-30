from graphql import GraphQLObjectType, GraphQLSchema


def Schema(models):
    return GraphQLSchema(
        query=GraphQLObjectType(
            name="RootQueryType",
            fields={
            },
        )
    )
