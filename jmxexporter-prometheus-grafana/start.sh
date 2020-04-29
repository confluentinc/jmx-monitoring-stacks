#!/bin/bash

. ../helper/configure_cp_demo.sh

echo -e "Launch cp-demo in $CP_DEMO_HOME and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/start.sh)

echo -e "Create user and certificates for kafkaLagExporter"
KAFKA_LAG_EXPORTER="User:kafkaLagExporter"
mkdir -p $MONITORING_STACK/assets/prometheus/security
cd $MONITORING_STACK/assets/prometheus/security
rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12
ROOT_CA_DIR=$PWD $CP_DEMO_HOME/scripts/security/certs-create-per-user.sh kafkaLagExporter

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
