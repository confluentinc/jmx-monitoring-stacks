#!/usr/bin/env bash

# Check if docker-compose exists
if command -v docker-compose &> /dev/null
then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

# Cleanup
$DOCKER_COMPOSE_CMD \
    --profile replicator \
    --profile schema-registry \
    --profile ksqldb \
    --profile consumer \
    --profile consumer-minimal \
    --profile schema-registry-primary-secondary \
    --profile jr \
    -f docker-compose.yaml \
    -f docker-compose.replicator.yaml \
    -f docker-compose.schema-registry.yaml \
    -f docker-compose.ksqldb.yaml \
    -f docker-compose.consumer.yaml \
    -f docker-compose.consumer-minimal.yaml \
    -f docker-compose.schema-registry-primary-secondary.yaml \
    -f docker-compose.jr.yaml \
    -f docker-compose.clusterlinking.yaml \
    -f docker-compose.connect.yaml \
    down -v
rm -rf jmx-exporter
rm -rf assets
GRAFANA_IMPORT_FOLDER=../jmxexporter-prometheus-grafana/assets/grafana/provisioning/import
rm -rf ${GRAFANA_IMPORT_FOLDER}
