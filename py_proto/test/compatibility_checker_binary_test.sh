#!/usr/bin/env bash
set -euxo pipefail

./src/compatibility_checker_binary ./test/resources/single_message.proto ./test/resources/empty.proto
