"""
rules_vitest_extension: a MODULE.lock.bazel extension that defines the @rules_vitest repository.
"""

load("//tools/build_rules/rules_vitest:rules_vitest.bzl", "rules_vitest_dependency")

def _rules_vitest_impl(_ctx):
    rules_vitest_dependency()

rules_vitest_extension = module_extension(
    implementation = _rules_vitest_impl,
)
