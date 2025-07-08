"""
rules_hugo_extension: a MODULE.lock.bazel extension that defines the @rules_hugo repository.
"""

load("//tools/build_rules/rules_hugo:rules_hugo.bzl", "rules_hugo_dependency")

def _rules_hugo_impl(_ctx):
    rules_hugo_dependency()

rules_hugo_extension = module_extension(
    implementation = _rules_hugo_impl,
)
