"""
rules_hugo_extension: a MODULE.lock.bazel extension that defines the @rules_hugo repository.
"""

# load("@bazel_tools//tools/build_defs/repo:local.bzl", "local_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_HUGO_COMMIT = "4648f26b5dbad4c107056b346f934d2a6d22b116"
RULES_HUGO_SHA256 = "8d17baf94bc41d415b04d942388e5cda63700c793e5d424100daa522709fd00b"

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
