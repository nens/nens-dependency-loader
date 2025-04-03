#!/bin/bash
set -e
set -u

VERSION=$(grep "^version" metadata.txt| cut -d= -f2)

ARTIFACT=nens_dependency_loader.${VERSION}.zip
PROJECT=nens-dependency-loader

# Rename generated zip to include version number.
cp nens_dependency_loader.zip ${ARTIFACT}

curl -X POST \
     --retry 3 \
     -H "Content-Type: multipart/form-data" \
     -F key=${NENS_DEPENDENCY_LOADER_ARTIFACTS_KEY} \
     -F artifact=@${ARTIFACT} \
     -F branch=${GITHUB_REF} \
     https://artifacts.lizard.net/upload/${PROJECT}/
