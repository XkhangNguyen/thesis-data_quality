#!/bin/bash

# Ensure a version number is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1
IMAGE_NAME="xkhangnguyen/data-quality"

# Build the new version
docker build -t $IMAGE_NAME:$VERSION .

# Tag the new version as latest
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

# Push both the new version and latest tag
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Successfully released $IMAGE_NAME:$VERSION and updated $IMAGE_NAME:latest"
