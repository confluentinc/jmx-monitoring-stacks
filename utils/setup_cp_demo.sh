#!/bin/bash

DEFAULT_CP_DEMO_HOME=$(realpath ${MONITORING_STACK}/../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

[ -d "${CP_DEMO_HOME}" ] || {
  echo "ERROR: ${CP_DEMO_HOME} does not exist. Have you cloned https://github.com/confluentinc/cp-demo? If cp-demo is not in ${CP_DEMO_HOME}, you can set CP_DEMO_HOME and try again."
  exit 1
}
CP_DEMO_VERSION=$(grep "CONFLUENT_DOCKER_TAG" "${CP_DEMO_HOME}/env_files/config.env")

export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"
