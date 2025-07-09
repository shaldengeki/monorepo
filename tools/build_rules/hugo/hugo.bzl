"""
hugo_dependency: a MODULE.lock.bazel extension that defines the @hugo repository.
"""

load("@rules_hugo//hugo:rules.bzl", "hugo_repository")

def hugo_dependency():
    #
    # Load hugo binary itself
    #
    # Optionally, load a specific version of Hugo, with the 'version' argument
    hugo_repository(
        name = "hugo",
        version = "0.127.0",
        sha256 = "3cf961de9831c0f2ac0e67eabc83251916ae8729292fa85ffa140e59bcbea8c0",
    )
