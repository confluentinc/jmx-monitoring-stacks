#!/bin/bash

DEFAULT_CP_DEMO_HOME=$(realpath ../../cp-demo)
CP_DEMO_HOME=${CP_DEMO_HOME:-$DEFAULT_CP_DEMO_HOME}

echo "Using cp-demo in $CP_DEMO_HOME"

export MONITORING_STACK=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export COMPOSE_FILE="$CP_DEMO_HOME/docker-compose.yml:$MONITORING_STACK/docker-compose.override.yml"

echo -e "Launch CP - demo"
(cd $CP_DEMO_HOME && ./scripts/start.sh)

echo -e "Create user and certificates for kafkaLagExporter"
KAFKA_LAG_EXPORTER="User:kafkaLagExporter"
cd $MONITORING_STACK/assets/prometheus/security
mkdir -p $MONITORING_STACK/assets/prometheus/security
rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12
$CP_DEMO_HOME/scripts/security/certs-create-per-user.sh kafkaLagExporter

cd $CP_DEMO_HOME

KAFKA_CLUSTER_ID=$(docker-compose exec zookeeper zookeeper-shell zookeeper:2181 get /cluster/id 2> /dev/null | grep \"version\" | jq -r .id)

echo "Creating role bindings for kafka lag exporter"
docker-compose exec tools bash -c "confluent iam rolebinding create \
    --principal $KAFKA_LAG_EXPORTER \
    --role SystemAdmin \
    --kafka-cluster-id $KAFKA_CLUSTER_ID"

docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nView Grafana dashboards at (admin/admin) ->"
echo -e "http://localhost:3000"
