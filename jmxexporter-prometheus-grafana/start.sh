#!/bin/bash

########################################
# Start cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
export OVERRIDE_PATH="${MONITORING_STACK}/docker-compose.override.yaml"

while test $# != 0 
do
    case "$1" in
    --test) echo "Detected test Flag. Last detected flag will be honoured." ; export OVERRIDE_PATH="${OVERRIDE_PATH}:${MONITORING_STACK}/docker-compose.testing.yaml" ;;
    --local) echo "Detected local Flag. Last detected flag will be honoured." ; export OVERRIDE_PATH="${OVERRIDE_PATH}:${MONITORING_STACK}/docker-compose.local.yaml" ;;
    esac
    shift
done
echo "Using ${OVERRIDE_PATH} for docker-compose override"

. $MONITORING_STACK/../utils/setup_cp_demo.sh

echo -e "Launch cp-demo in $CP_DEMO_HOME (version $CP_DEMO_VERSION) and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/start.sh)

########################################
# Start monitoring solution
########################################

echo -e "Create user and certificates for kafkaLagExporter"
KAFKA_LAG_EXPORTER="User:kafkaLagExporter"
SECURITY_DIR="${MONITORING_STACK}/assets/security"
mkdir -p $SECURITY_DIR
(cd $SECURITY_DIR && rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12)
(cd $SECURITY_DIR && $CP_DEMO_HOME/scripts/security/certs-create-per-user.sh kafkaLagExporter)

echo -e "Create role binding for kafkaLagExporter"
cd $CP_DEMO_HOME
KAFKA_CLUSTER_ID=$(docker-compose exec zookeeper zookeeper-shell zookeeper:2181 get /cluster/id 2> /dev/null | grep \"version\" | jq -r .id)
docker-compose exec tools bash -c "confluent iam rbac role-binding create \
    --principal $KAFKA_LAG_EXPORTER \
    --role SystemAdmin \
    --kafka-cluster-id $KAFKA_CLUSTER_ID"

echo -e "Launch $MONITORING_STACK"
docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nView Grafana dashboards at (admin/password) ->"
echo -e "http://localhost:3000"


while test $# != 0 
do
    case "$1" in
    --test) echo "Auto testing is not implemented yet. Please use the --local flag to invoke the test script manually." ;;
    --local) echo "Detected local Flag. Will wait for about 150 seconds before executing the testing script." ; sleep 150 ; base_stacks_dir="$(dirname "${MONITORING_STACK}")" ; ${MONITORING_STACK}/../utils/testing/code/main.py --jmx-monitoring-stacks-base-fullpath ${base_stacks_dir} ;;
    esac
    shift
done
