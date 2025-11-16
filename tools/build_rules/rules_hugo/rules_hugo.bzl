"""
rules_hugo_extension: a MODULE.lock.bazel extension that defines the @rules_hugo repository.
"""

# load("@bazel_tools//tools/build_defs/repo:local.bzl", "local_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_HUGO_COMMIT = "a3f29dd4ca21a54ee7403710323dcd89e15cd8d2"
RULES_HUGO_SHA256 = "90e94cffee0ac2d923eec1f6996bd854485d5724c8e46f21e28e3c445cf20020"

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
