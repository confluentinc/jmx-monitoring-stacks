#!/bin/bash

########################################
# Stop cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

export OUTPUT_FILE=$MONITORING_STACK/assets/prometheus/prometheus-config/prometheus.yml
export DOCKER_COMPOSE_FILE=$MONITORING_STACK/docker-compose.yaml

echo -e "Removing file $OUTPUT_FILE "
[[ -e $OUTPUT_FILE ]]; rm -f $OUTPUT_FILE 
echo -e "STOP $MONITORING_STACK"
docker-compose -f $MONITORING_STACK/docker-compose.yaml down

echo -e "Removing file $DOCKER_COMPOSE_FILE "
[[ -e $DOCKER_COMPOSE_FILE ]]; rm -f $DOCKER_COMPOSE_FILE