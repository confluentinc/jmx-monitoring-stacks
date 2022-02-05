#!/bin/bash

########################################
# Stop cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

export OUTPUT_FILE=$MONITORING_STACK/assets/prometheus/prometheus-config/prometheus.yml
echo -e "Removing file $OUTPUT_FILE "
[[ -e $OUTPUT_FILE ]]; rm -f $OUTPUT_FILE 
echo -e "STOP $MONITORING_STACK"
docker-compose -f $MONITORING_STACK/docker-compose.yaml down
