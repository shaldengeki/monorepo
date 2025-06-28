"""
defs.bzl: public interfaces for API rules.

You should import rules exposed here.
"""

load("//tools/build_rules/api:graphql_api_image.bzl", _graphql_api_image = "graphql_api_image")
load("//tools/build_rules/api/migrations:defs.bzl", _api_migrations = "migrations")

graphql_api_image = _graphql_api_image
api_migrations = _api_migrations
