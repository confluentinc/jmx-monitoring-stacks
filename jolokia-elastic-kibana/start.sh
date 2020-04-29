#!/bin/bash

. ../helper/fullpath.sh

DEFAULT_CP_DEMO_HOME=$(fullpath ../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

echo "Using cp-demo in $CP_DEMO_HOME"

export MONITORING_STACK=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"

echo -e "Launch CP - demo"
cd $CP_DEMO_HOME
./scripts/start.sh

echo -e "Starting jmx-data-poller"
docker-compose up -d jmx-data-poller

echo -e "\nView Kibana dashboards at ->"
echo -e "http://localhost:5601/app/kibana#/dashboards\n"
