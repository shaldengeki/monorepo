#!/usr/bin/env bash
set -euxo pipefail
./src/parser_binary ./test/resources/empty.proto

GOOGLE_PROTOS=$(find ./external/com_google_protobuf/src/google/protobuf -name "any.proto")
for f in $GOOGLE_PROTOS; do
    ./src/parser_binary $f
done
