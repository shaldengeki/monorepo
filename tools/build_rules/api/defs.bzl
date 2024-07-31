"""
defs.bzl: public interfaces for API rules.

You should import rules exposed here.
"""

load("//tools/build_rules/api:api_image.bzl", _api_image = "api_image")
load("//tools/build_rules/api/migrations:defs.bzl", _api_migrations = "migrations")

api_image = _api_image
api_migrations = _api_migrations
