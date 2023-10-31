#!/bin/bash

########################################
# Start demo-scene - cluster linking-disaster-recovery
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
export OVERRIDE_PATH="${MONITORING_STACK}/docker-compose.override.yaml"


echo "Using ${OVERRIDE_PATH} for docker-compose override"

. $MONITORING_STACK/../../utils/setup_cluster-linking_demo.sh

echo -e "Launch clink-demo in CLINK_DEMO_HOME monitoring stack in $MONITORING_STACK"
(cd $CLINK_DEMO_HOME && docker-compose up -d)

echo -e "Wait 30 seconds to start up..."

########################################
# Create resources
########################################

sleep 30

docker exec mainKafka kafka-topics --bootstrap-server mainKafka:19092 --topic product --create --partitions 1 --replication-factor 1

echo -e "Create link main-to-disaster-cl"

docker exec disasterKafka bash -c '\
echo "\
bootstrap.servers=mainKafka:19092
" > /home/appuser/cl.properties'

docker exec disasterKafka kafka-cluster-links --bootstrap-server disasterKafka:29092 --create --link main-to-disaster-cl --config-file /home/appuser/cl.properties

docker exec disasterKafka kafka-mirrors --create --source-topic product --mirror-topic product --link main-to-disaster-cl --bootstrap-server disasterKafka:29092

echo -e "Verify link main-to-disaster-cl"

docker exec disasterKafka kafka-cluster-links --bootstrap-server disasterKafka:29092 --link main-to-disaster-cl --list

########################################
# Start monitoring solution
########################################

echo -e "Launch $MONITORING_STACK"
docker-compose up -d prometheus node-exporter grafana

echo -e "\nView Grafana dashboards at (admin/password) ->"
echo -e "http://localhost:3000"
