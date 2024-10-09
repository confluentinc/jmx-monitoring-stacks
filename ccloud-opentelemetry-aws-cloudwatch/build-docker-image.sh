#!/bin/bash

set -x

# Build
docker build -t otel-collector .

# Run 
# docker run -p 4317:4317 -p 4318:4318 -p 8888:8888 -p 8889:8889 -p 13133:13133 \
# -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> \
# -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> \
# otel-collector