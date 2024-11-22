#!/usr/bin/env bash

echo -e "\ndev-toolkit bootstrap..."

# Check if docker-compose exists
if command -v docker-compose &> /dev/null
then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

# get args from command line (if any) and put them in a variable
docker_args=("$@")
echo "docker_args: ${docker_args[@]}"

mkdir -p assets/prometheus
mkdir -p assets/grafana/provisioning/dashboards assets/grafana/provisioning/datasources

echo -e "Create dashboards for auto import in grafana"
MONITORING_STACK=../jmxexporter-prometheus-grafana
GRAFANA_IMPORT_FOLDER=${MONITORING_STACK}/assets/grafana/provisioning/import
mkdir -p ${GRAFANA_IMPORT_FOLDER}/dashboards ${GRAFANA_IMPORT_FOLDER}/datasources
cp -rf ${MONITORING_STACK}/assets/grafana/provisioning/datasources/datasource.yml ${GRAFANA_IMPORT_FOLDER}/datasources/datasource.yml
cp -rf ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/dashboard.yml ${GRAFANA_IMPORT_FOLDER}/dashboards/dashboard.yml
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/cluster-linking.json >${GRAFANA_IMPORT_FOLDER}/dashboards/cluster-linking.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-oracle-cdc.json >${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-oracle-cdc.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-platform-kraft.json >${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-platform.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-rbac.json >${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-rbac.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/rest-proxy.json >${GRAFANA_IMPORT_FOLDER}/dashboards/rest-proxy.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-cluster-kraft.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-connect-cluster.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-connect-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-consumer.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-consumer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-lag-exporter.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-lag-exporter.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-producer.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-producer.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-quotas.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-quotas.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-stream.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-stream.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-streams-rocksdb.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-streams-rocksdb.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-topics-kraft.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-topics.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kafka-transaction-coordinator.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kafka-transaction-coordinator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/kraft.json >${GRAFANA_IMPORT_FOLDER}/dashboards/kraft.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/ksqldb-cluster.json >${GRAFANA_IMPORT_FOLDER}/dashboards/ksqldb-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/replicator.json >${GRAFANA_IMPORT_FOLDER}/dashboards/replicator.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/schema-registry-cluster.json >${GRAFANA_IMPORT_FOLDER}/dashboards/schema-registry-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/tiered-storage.json >${GRAFANA_IMPORT_FOLDER}/dashboards/tiered-storage.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/zookeeper-cluster.json >${GRAFANA_IMPORT_FOLDER}/dashboards/zookeeper-cluster.json
sed 's/${Prometheus}/Prometheus/g' ${MONITORING_STACK}/assets/grafana/provisioning/dashboards/confluent-audit.json >${GRAFANA_IMPORT_FOLDER}/dashboards/confluent-audit.json


# Copy needed files in the current folder
cp -R ../shared-assets/jmx-exporter .
cp -R ${MONITORING_STACK}/assets/prometheus/prometheus-config ./assets/prometheus
cp -R ${GRAFANA_IMPORT_FOLDER}/dashboards/* ./assets/grafana/provisioning/dashboards
cp -R ${GRAFANA_IMPORT_FOLDER}/datasources/* ./assets/grafana/provisioning/datasources

# ADD client monitoring to prometheus config
cat <<EOF >>assets/prometheus/prometheus-config/prometheus.yml


  - job_name: 'spring-client'
    static_configs:
      - targets: ['spring-client:9191']
        labels:
          env: "dev"

  - job_name: 'consumer'
    static_configs:
      - targets: ['consumer-ok:1234', 'consumer-faulty:1234']
        labels:
          env: "dev"
EOF

# ADD KRaft monitoring to prometheus config
cat <<EOF >>assets/prometheus/prometheus-config/prometheus.yml


  - job_name: 'kafka-controller'
    static_configs:
      - targets: ['kafka1:1234', 'kafka2:1234', 'kafka3:1234']
        labels:
          env: "dev"
EOF

# ADD Brokers monitoring to prometheus config (default was for 2 brokers only)
cat <<EOF >>assets/prometheus/prometheus-config/prometheus.yml

  - job_name: "kafka-broker-2"
    static_configs:
      - targets:
          - "kafka3:1234"
          - "kafka4:1234"
        labels:
          env: "dev"
          job: "kafka-broker"
    relabel_configs:
      - source_labels: [__address__]
        target_label: hostname
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'
EOF

# ADD Schema Registry monitoring to prometheus config (default was for 1 SR only)
cat <<EOF >>assets/prometheus/prometheus-config/prometheus.yml

  - job_name: "schema-registry-2"
    static_configs:
      - targets:
          - "schemaregistry2:1234"
        labels:
          env: "dev"
          job: "schema-registry"
    relabel_configs:
      - source_labels: [__address__]
        target_label: hostname
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'
EOF

echo -e "\nStarting profiles..."

# Start the development environment
$DOCKER_COMPOSE_CMD ${docker_args[@]} \
  -f docker-compose.yaml \
  -f docker-compose.replicator.yaml \
  -f docker-compose.schema-registry.yaml \
  -f docker-compose.ksqldb.yaml \
  -f docker-compose.consumer.yaml \
  -f docker-compose.consumer-minimal.yaml \
  -f docker-compose.schema-registry-primary-secondary.yaml \
  -f docker-compose.jr.yaml \
  up -d

# if docker_args contains replicator, then start the replicator
if [[ " ${docker_args[@]} " =~ " replicator " ]]; then
  echo -e "\nWaiting 120 seconds before starting replicator connector..."
  sleep 120
  echo -e "\nStarting replicator connector..."

  curl --request PUT \
    --url http://localhost:8083/connectors/replicator/config \
    --header 'content-type: application/json' \
    --header 'user-agent: vscode-restclient' \
    --data '{"connector.class": "io.confluent.connect.replicator.ReplicatorSourceConnector","topic.regex": "quotes","key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","header.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","src.kafka.bootstrap.servers": "kafka1:29092,kafka2:29092,kafka3:29092,kafka4:29092","dest.kafka.bootstrap.servers": "broker-replicator-dst:29092","error.tolerance": "all","errors.log.enable": "true","errors.log.include.messages": "true","confluent.topic.replication.factor": 1,"provenance.header.enable": "true","topic.timestamp.type": "LogAppendTime","topic.rename.format": "replica-${topic}","tasks.max": "1"}'

  echo -e "\nWaiting 45 seconds to initialize replicator connector..."
  sleep 45
fi

echo -e "\ndev-toolkit started!"

# Look at Prometheus metrics
echo -e "\nView Prometheus metrics at ->"
echo -e "http://localhost:9090"

# Look at Grafana dashboards
echo -e "\nView Grafana dashboards at (admin/password) ->"
echo -e "http://localhost:3000"

# Print message to apply quotas if needed
echo -e "\nRun the following command if you want to add quotas (this will make few metrics available) ->"
echo -e "docker exec kafka1 bash -c \"KAFKA_OPTS= kafka-configs --bootstrap-server kafka1:29092 --alter --add-config 'producer_byte_rate=10485760,consumer_byte_rate=10485760' --entity-type clients --entity-default\""