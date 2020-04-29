#!/bin/bash

DEFAULT_CP_DEMO_HOME="../../cp-demo"
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

echo "Using cp-demo in $CP_DEMO_HOME"

[ -d "${CP_DEMO_HOME}" ] || echo "Error: ${CP_DEMO_HOME} does not exists. Have you cloned the cp-demo repository ? If cp-demo is in a different directory you can configure CP_DEMO_HOME variable)."

CP_DEMO_VERSION=$(grep CONFLUENT_DOCKER_TAG $CP_DEMO_HOME/env_files/config.env)
echo "Using version $CP_DEMO_VERSION" 

. $CP_DEMO_HOME/scripts/helper/fullpath.sh

#let's work with full path to avoid any issues
CP_DEMO_HOME=$(fullpath $CP_DEMO_HOME)

# we use $0 here to make sure we take the value from the root level
export MONITORING_STACK=$(fullpath $(dirname $0))
export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"
