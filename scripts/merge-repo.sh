#!/usr/bin/env bash
set -euxo pipefail

REPO=$1
cd ~
rm -rf $REPO
git clone https://github.com/shaldengeki/$REPO

(
    cd $REPO
    time git filter-repo --to-subdirectory-filter $REPO
)

(
    cd ~/monorepo/
    git switch main
    git remote add $REPO ../$REPO
    git fetch $REPO --no-tags
    EDITOR=true git merge --allow-unrelated-histories $REPO/main
    git remote remove $REPO
)
