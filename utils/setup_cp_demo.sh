#!/bin/bash

# This method does a job similar to realpath, but avoid that extra dependency.
# It returns fullpath for a given parameter to avoind using relative paths.
fullpath ()
{
   fullpath=$(cd $1 && pwd -P)
   echo $fullpath
   cd $OLDPWD
}

DEFAULT_CP_DEMO_HOME=$(fullpath ${MONITORING_STACK}/../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

[ -d "${CP_DEMO_HOME}" ] || {
  echo "ERROR: ${CP_DEMO_HOME} does not exist. Have you cloned https://github.com/confluentinc/cp-demo? If cp-demo is not in ${CP_DEMO_HOME}, you can set CP_DEMO_HOME and try again."
  exit 1
}
CP_DEMO_VERSION=$(grep "CONFLUENT_DOCKER_TAG" "${CP_DEMO_HOME}/env_files/config.env")

if [[ -z "${OVERRIDE_PATH}" ]]; then
  OVERRIDE_PATH="${MONITORING_STACK}/docker-compose.override.yaml"
fi 

export COMPOSE_FILE="${CP_DEMO_HOME}/docker-compose.yml:${OVERRIDE_PATH}"
