from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLSchema,
    GraphQLString
)

schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'hello': GraphQLField(
                GraphQLString,
                resolver=lambda *args: 'world'
            )
        }
    )
)
