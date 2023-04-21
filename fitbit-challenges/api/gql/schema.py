from graphql import GraphQLObjectType, GraphQLSchema, GraphQLField, GraphQLString

from .types.workweek_hustle import challenges_field, create_workweek_hustle_field


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
                ),
                "challenges": challenges_field(models.WorkweekHustle),
            },
        ),
        mutation=GraphQLObjectType(
            name="Mutation",
            fields={
                "createWorkweekHustle": create_workweek_hustle_field(
                    models.WorkweekHustle
                ),
            },
        ),
    )
