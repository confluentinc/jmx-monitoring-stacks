#!/usr/bin/env bash

# Cleanup
docker-compose --profile replicator -f docker-compose.yaml -f docker-compose.replicator.yaml down -v
rm -rf jmx-exporter
rm -rf assets
GRAFANA_IMPORT_FOLDER=../jmxexporter-prometheus-grafana/assets/grafana/provisioning/import
rm -rf ${GRAFANA_IMPORT_FOLDER}