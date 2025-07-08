"""
rules_hugo_extension: a MODULE.lock.bazel extension that defines the @rules_hugo repository.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_HUGO_COMMIT = "7c3e323e4c5519d056d76bb4495434d23bd1241a"
RULES_HUGO_SHA256 = "2c014fd73be6a74e64c42e294d32593ad4ceec5089d383e27f03b3f488b42892"

def rules_hugo_dependency():
    http_archive(
        name = "rules_hugo",
        url = "https://github.com/shaldengeki/rules_hugo/archive/%s.zip" % RULES_HUGO_COMMIT,
        sha256 = RULES_HUGO_SHA256,
        strip_prefix = "rules_hugo-%s" % RULES_HUGO_COMMIT,
    )
