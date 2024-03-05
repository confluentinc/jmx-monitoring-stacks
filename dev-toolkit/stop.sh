#!/usr/bin/env bash

# Cleanup
docker-compose \
    --profile replicator \
    --profile schema-registry \
    --profile ksqldb \
    --profile consumer \
    -f docker-compose.yaml \
    -f docker-compose.replicator.yaml \
    -f docker-compose.schema-registry.yaml \
    -f docker-compose.ksqldb.yaml \
    -f docker-compose.consumer.yaml \
    down -v
rm -rf jmx-exporter
rm -rf assets
GRAFANA_IMPORT_FOLDER=../jmxexporter-prometheus-grafana/assets/grafana/provisioning/import
rm -rf ${GRAFANA_IMPORT_FOLDER}
