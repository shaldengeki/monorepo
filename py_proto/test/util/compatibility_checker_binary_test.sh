#!/usr/bin/env bash
set -euxo pipefail

./src/util/compatibility_checker_binary ./test/resources/empty.proto ./test/resources/single_message.proto
