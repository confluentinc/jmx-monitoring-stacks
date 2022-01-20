#!/bin/bash

########################################
# Stop cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo -e "STOP $MONITORING_STACK"
docker-compose -f $MONITORING_STACK/docker-compose.yml down
