#!/usr/bin/env bash
set -euxo pipefail

./src/python/py_proto/util/compatibility_checker_binary ./src/python/py_proto/test/resources/empty.proto ./src/python/py_proto/test/resources/single_message.proto
