#!/bin/bash

DEFAULT_CP_DEMO_HOME=$(realpath ../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

export MONITORING_STACK=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"

echo -e "Stop cp-demo in $CP_DEMO_HOME and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/stop.sh)
