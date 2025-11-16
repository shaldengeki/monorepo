"""
rules_hugo_extension: a MODULE.lock.bazel extension that defines the @rules_hugo repository.
"""

# load("@bazel_tools//tools/build_defs/repo:local.bzl", "local_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_HUGO_COMMIT = "7bcb5633f34fc84c5c2a76d1a29f587db1784d0e"
RULES_HUGO_SHA256 = "bd61125bff6e94d83b611c8e52e4e2caf11e8b0beaa53521960f5b2930eb6d1d"

def rules_hugo_dependency():
    # local_repository(
    #     name = "rules_hugo",
    #     path = "../rules_hugo"
    # )
    http_archive(
        name = "rules_hugo",
        url = "https://github.com/shaldengeki/rules_hugo/archive/%s.zip" % RULES_HUGO_COMMIT,
        sha256 = RULES_HUGO_SHA256,
        strip_prefix = "rules_hugo-%s" % RULES_HUGO_COMMIT,
    )
