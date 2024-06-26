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

########################################
# Starting the librdkafka based example
########################################
echo "Creating role binding librdkafka application"
docker-compose exec tools bash -c "/tmp/helper-librdkafka/create-resources.sh" || exit 1

docker build -t librdkafka-application -f $MONITORING_STACK/librdkafka/Dockerfile $MONITORING_STACK/librdkafka
docker-compose up --no-recreate -d librdkafka

echo -e "Create dashboards for auto import in grafana"
GRAFANA_IMPORT_FOLDER=${MONITORING_STACK}/assets/grafana/provisioning/import
mkdir -p ${GRAFANA_IMPORT_FOLDER}/dashboards ${GRAFANA_IMPORT_FOLDER}/datasources
cp -rf ${MONITORING_STACK}/assets/grafana/provisioning/datasources/datasource.yml ${GRAFANA_IMPORT_FOLDER}/datasources/datasource.yml
cp -rf ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/dashboard.yml ${GRAFANA_IMPORT_FOLDER}/dashboards/dashboard.yml
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/cluster-linking.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/cluster-linking.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-oracle-cdc.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-oracle-cdc.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-platform.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-platform.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-rbac.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-rbac.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/rest-proxy.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/rest-proxy.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-connect-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-connect-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-consumer.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-consumer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-lag-exporter.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-lag-exporter.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-producer.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-producer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-quotas.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-quotas.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-stream.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-stream.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-streams-rocksdb.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-streams-rocksdb.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-topics.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-topics.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-transaction-coordinator.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-transaction-coordinator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kraft.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kraft.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/ksqldb-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/ksqldb-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/replicator.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/replicator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/schema-registry-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/schema-registry-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/tiered-storage.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/tiered-storage.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/zookeeper-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/zookeeper-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/librdkafka-application.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/librdkafka-application.json

echo -e "Launch $MONITORING_STACK"
docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana


echo -e "\nView Prometheus at ->"
echo -e "http://localhost:9090"

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