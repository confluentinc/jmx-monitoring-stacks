#!/bin/bash

########################################
# Start cp-demo
########################################

DEFAULT_CP_DEMO_HOME=$(realpath ../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

export MONITORING_STACK=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"

echo -e "Launch cp-demo in $CP_DEMO_HOME and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/start.sh)


########################################
# Start monitoring solution
########################################

echo -e "Create user and certificates for kafkaLagExporter"
KAFKA_LAG_EXPORTER="User:kafkaLagExporter"
SECURITY_DIR="${MONITORING_STACK}/assets/prometheus/security"
mkdir -p $SECURITY_DIR
(cd $SECURITY_DIR && rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12)
(cd $SECURITY_DIR && $CP_DEMO_HOME/scripts/security/certs-create-per-user.sh kafkaLagExporter)

echo -e "Create role binding for kafkaLagExporter"
cd $CP_DEMO_HOME
KAFKA_CLUSTER_ID=$(docker-compose exec zookeeper zookeeper-shell zookeeper:2181 get /cluster/id 2> /dev/null | grep \"version\" | jq -r .id)
docker-compose exec tools bash -c "confluent iam rolebinding create \
    --principal $KAFKA_LAG_EXPORTER \
    --role SystemAdmin \
    --kafka-cluster-id $KAFKA_CLUSTER_ID"

echo -e "Launch $MONITORING_STACK"
docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nView Grafana dashboards at (admin/admin) ->"
echo -e "http://localhost:3000"
