from typing import Any, Optional, Type

from flask import Flask
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLField,
    GraphQLFloat,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
)

from skeleton.config import app, db
from skeleton.models import ExampleModel


def example_model_fields() -> dict[str, GraphQLField]:
    return {
        "id": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description="The id of the example model.",
        ),
    }


example_model_type = GraphQLObjectType(
    "ExampleModel",
    description="A example model.",
    fields=example_model_fields,
)


def fetch_example_model(
    example_model: Type[ExampleModel], params: dict[str, Any]
) -> Optional[ExampleModel]:
    return (example_model.query.filter(example_model.id == params["id"])).first()


example_model_filters: dict[str, GraphQLArgument] = {
    "id": GraphQLArgument(
        GraphQLNonNull(GraphQLInt),
        description="ID of the example model.",
    ),
}


def example_model_field(example_model: type[ExampleModel]) -> GraphQLField:
    return GraphQLField(
        example_model_type,
        args=example_model_filters,
        resolve=lambda root, info, **args: fetch_example_model(example_model, args),
    )
