#!/usr/bin/env bash
set -euxo pipefail

./py_proto/util/compatibility_checker_binary ./py_proto/test/resources/empty.proto ./py_proto/test/resources/single_message.proto
