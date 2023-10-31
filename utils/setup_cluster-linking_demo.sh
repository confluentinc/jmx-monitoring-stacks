#!/bin/bash

# This method does a job similar to realpath, but avoid that extra dependency.
# It returns fullpath for a given parameter to avoind using relative paths.
fullpath ()
{
   fullpath=$(cd $1 && pwd -P)
   echo $fullpath
   cd $OLDPWD
}

DEFAULT_CLINK_DEMO_HOME=$(fullpath ${MONITORING_STACK}/../../../clink-demo)
CLINK_DEMO_HOME=${DEFAULT_CLINK_DEMO_HOME}/cluster-linking-disaster-recovery

[ -d "${CLINK_DEMO_HOME}" ] || {
  echo "ERROR: ${CLINK_DEMO_HOME} does not exist. Have you cloned https://github.com/confluentinc/demo-scene? If demo-scene is not in ${CLINK_DEMO_HOME}, you can set CLINK_DEMO_HOME and try again."
  exit 1
}

if [[ -z "${OVERRIDE_PATH}" ]]; then
  OVERRIDE_PATH="${MONITORING_STACK}/docker-compose.override.yaml"
fi 

export COMPOSE_FILE="${CLINK_DEMO_HOME}/docker-compose.yml:${OVERRIDE_PATH}"
