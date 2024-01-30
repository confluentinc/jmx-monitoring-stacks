#!/bin/bash

########################################
# Start cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
export OVERRIDE_PATH="${MONITORING_STACK}/docker-compose.override.yaml"


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
docker-compose up -d influxdb kafka-lag-exporter

echo -e "Waiting 15 seconds for influxdb to start"

sleep 15

echo -e "Setup influxdb"
docker exec influxdb bash -c "influx setup --host http://influxdb:8086 --username admin --password password --token AAAAA --org dev --bucket dev --force"

echo -e "Import influxdb templates"
docker exec influxdb bash -c "influx apply -f /tmp/template/kafka_cluster.yaml --host http://influxdb:8086 --token AAAAA --org dev --force yes"

echo -e "Setup telegraf"
docker-compose up -d telegraf

echo -e "\nView InfluxDB dashboards at (admin/password) ->"
echo -e "http://localhost:9086"