"""
defs.bzl: public interfaces for worker rules.

You should import rules exposed here.
"""

load("//tools/build_rules/worker:worker.bzl", _worker = "worker")

worker = _worker
