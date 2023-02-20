#!/usr/bin/env bash
set -euo pipefail

echo "Local protos:"
LOCAL_PROTOS=$(find ./test/resources -name "*.proto" | sort)
for f in $LOCAL_PROTOS; do
    echo $f
    ./src/util/parser_binary $f > /dev/null
done

echo "Google protos:"
GOOGLE_PROTOS=$(find ./external/com_google_protobuf/src/google/protobuf -name "*.proto" | xargs grep --files-without-match "proto2" | sort)
for f in $GOOGLE_PROTOS; do
    echo $f
    ./src/util/parser_binary $f > /dev/null
done
