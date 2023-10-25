#!/usr/bin/env bash

# Cleanup
docker-compose down -v
rm -rf jmx-exporter
rm -rf assets