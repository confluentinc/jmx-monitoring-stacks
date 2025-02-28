#!/usr/bin/env bash

# Check if docker-compose exists
if command -v docker-compose &> /dev/null
then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

# get args from command line (if any) and put them in a variable
docker_args=("$@")
echo "docker_args: ${docker_args[@]}"

# if docker_args contains tieredstorage, then create topics required for tieredstorage
if [[ " ${docker_args[@]} " =~ " tieredstorage " ]]; then
  echo -e "\nWaiting 3 seconds before creating democp-bucket on minio..."
  $DOCKER_COMPOSE_CMD stop kafka1 kafka2 kafka3 kafka4 minio
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
    --profile clusterlinking \
    --profile kstream \
    --profile kui \
    --profile restproxy \
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
    -f docker-compose.kstream.yaml \
    -f docker-compose.kui.yaml \
    -f docker-compose.restproxy.yaml \
    down -v
rm -rf jmx-exporter
rm -rf assets
GRAFANA_IMPORT_FOLDER=../jmxexporter-prometheus-grafana/assets/grafana/provisioning/import
rm -rf ${GRAFANA_IMPORT_FOLDER}
