#!/bin/bash

################################################################################
# This connects to Kafka cluster, KsqlDB, Connector , SR running on cCloud
################################################################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

########################################
# Create prometheus scrape config from Environment variables
########################################
echo -e "Generate Prometheus Configuration from Environemnet variables for  $MONITORING_STACK"
export OUTPUT_FILE=$MONITORING_STACK/assets/prometheus/prometheus-config/prometheus.yml
echo " creating prometheus configuration file $OUTPUT_FILE "
[[ -e $OUTPUT_FILE ]]; rm -f $OUTPUT_FILE 
mkdir -p "$MONITORING_STACK/assets/prometheus/prometheus-config"
source $MONITORING_STACK/utils/env_variables.env
envsubst < $MONITORING_STACK/utils/prometheus-template.yml > $MONITORING_STACK/assets/prometheus/prometheus-config/prometheus.yml


########################################
# Start monitoring solution
########################################
echo -e "Launch $MONITORING_STACK"
docker-compose -f $MONITORING_STACK/docker-compose.yaml up -d prometheus  grafana

echo -e "\nView Grafana dashboards at (admin/password) ->"
echo -e "http://localhost:3000"
