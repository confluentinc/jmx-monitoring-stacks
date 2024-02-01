#!/bin/bash

########################################
# Stop demo-scene - cluster linking-disaster-recovery
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

. $MONITORING_STACK/../../utils/setup_cluster-linking_demo.sh


echo -e "Stop clink-demo in $CLINK_DEMO_HOME and monitoring stack in $MONITORING_STACK"

(cd $CLINK_DEMO_HOME && docker-compose down --volumes)

GRAFANA_IMPORT_FOLDER=${MONITORING_STACK}/../assets/grafana/provisioning/import
rm -rf ${GRAFANA_IMPORT_FOLDER}