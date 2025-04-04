#!/bin/bash
# We upload a zip to https://docs.3di.live/nens-dependency-loader-dev/
# for development purposes only.
set -e

BRANCH=${{ github.head_ref || github.ref_name }}

ARTIFACT=nens_dependency_loader-${BRANCH}.zip
PROJECT=nens_dependency_loader-dev

# Rename generated zip to include branch name.
cp nens_dependency_loader.zip ${ARTIFACT}

curl -X POST \
     --retry 3 \
     -H "Content-Type: multipart/form-data" \
     -F key=${NENS_DEPENDENCY_LOADER_DEV_ARTIFACTS_KEY} \
     -F artifact=@${ARTIFACT} \
     -F branch=${BRANCH} \
     https://artifacts.lizard.net/upload/${PROJECT}/
