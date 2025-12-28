"""
rules_vitest_extension: a MODULE.lock.bazel extension that defines the @rules_vitest repository.
"""

# load("@bazel_tools//tools/build_defs/repo:local.bzl", "local_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_VITEST_COMMIT = "b43de98fc06e33f33e0a1c54066bba51bce095a7"
RULES_VITEST_SHA256 = "c30126e02b47aab51072e56ce2544cadb19641a57b1f87b619c8b58b232e44cb"

def rules_vitest_dependency():
    # local_repository(
    #     name = "fremtind_rules_vitest",
    #     path = "../rules_vitest"
    # )
    http_archive(
        name = "fremtind_rules_vitest",
        url = "https://github.com/shaldengeki/rules_vitest/archive/%s.zip" % RULES_VITEST_COMMIT,
        sha256 = RULES_VITEST_SHA256,
        strip_prefix = "rules_vitest-%s" % RULES_VITEST_COMMIT,
    )
