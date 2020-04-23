#!/bin/bash

CP_DEMO_HOME=$(realpath ../../cp-demo)

export MONITORING_STACK=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export DOCKER_COMPOSE_OPTS="-f $CP_DEMO_HOME/docker-compose.yml -f $MONITORING_STACK/docker-compose.override.yml"

cd $CP_DEMO_HOME
./scripts/stop.sh
