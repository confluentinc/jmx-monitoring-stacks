#!/usr/bin/env bash

# Cleanup
docker-compose --profile replicator -f docker-compose.yaml -f docker-compose.replicator.yaml down -v
rm -rf jmx-exporter
rm -rf assets