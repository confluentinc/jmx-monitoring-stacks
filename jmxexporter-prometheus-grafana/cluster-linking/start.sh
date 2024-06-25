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

echo -e "Create dashboards for auto import in grafana"
GRAFANA_IMPORT_FOLDER=${MONITORING_STACK}/../assets/grafana/provisioning/import
mkdir -p ${GRAFANA_IMPORT_FOLDER}/dashboards ${GRAFANA_IMPORT_FOLDER}/datasources
cp -rf ${MONITORING_STACK}/../assets/grafana/provisioning/datasources/datasource.yml ${GRAFANA_IMPORT_FOLDER}/datasources/datasource.yml
cp -rf ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/dashboard.yml ${GRAFANA_IMPORT_FOLDER}/dashboards/dashboard.yml
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/cluster-linking.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/cluster-linking.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/confluent-oracle-cdc.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-oracle-cdc.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/confluent-platform.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-platform.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/confluent-rbac.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-rbac.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/rest-proxy.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/rest-proxy.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-connect-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-connect-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-consumer.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-consumer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-lag-exporter.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-lag-exporter.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-producer.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-producer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-quotas.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-quotas.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-stream.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-stream.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-streams-rocksdb.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-streams-rocksdb.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-topics.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-topics.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kafka-transaction-coordinator.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-transaction-coordinator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/kraft.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/kraft.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/ksqldb-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/ksqldb-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/replicator.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/replicator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/schema-registry-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/schema-registry-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/tiered-storage.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/tiered-storage.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/../assets/grafana/provisioning/dashboards/zookeeper-cluster.json > ${GRAFANA_IMPORT_FOLDER}/dashboards/zookeeper-cluster.json


########################################
# Start monitoring solution
########################################

echo -e "Launch $MONITORING_STACK"
docker-compose up -d prometheus node-exporter grafana

echo -e "\nView Grafana dashboards at (admin/password) ->"
echo -e "http://localhost:3000"
