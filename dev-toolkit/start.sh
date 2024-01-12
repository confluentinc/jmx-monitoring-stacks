#!/usr/bin/env bash

# get args from command line (if any) and put them in a variable
docker_args=("$@")
echo "docker_args: ${docker_args[@]}"

# Copy needed files in the current folder
cp -R ../shared-assets/jmx-exporter .
cp -R ../jmxexporter-prometheus-grafana/assets .

# Copy WIP dashboards
cp ./grafana-wip/* ./assets/grafana/provisioning/dashboards

# ADD client monitoring to prometheus config
cat <<EOF >> assets/prometheus/prometheus-config/prometheus.yml


  - job_name: 'spring-client'
    static_configs:
      - targets: ['spring-client:9191']
        labels:
          env: "dev"
EOF

# ADD KRaft monitoring to prometheus config
cat <<EOF >> assets/prometheus/prometheus-config/prometheus.yml


  - job_name: 'kafka-controller'
    static_configs:
      - targets: ['kafka1:1234', 'kafka2:1234', 'kafka3:1234']
        labels:
          env: "dev"
EOF

# Start the development environment
docker-compose ${docker_args[@]} -f docker-compose.yaml -f docker-compose.replicator.yaml up -d

# Look at Grafana dashboards
echo -e "\nView Grafana dashboards at (admin/grafana) ->"
echo -e "http://localhost:3000"

# if docker_args contains replicator, then start the replicator
if [[ " ${docker_args[@]} " =~ " replicator " ]]; then
  sleep 180
  echo -e "\nStarting replicator connector..."
  
  curl --request PUT \
  --url http://localhost:8083/connectors/replicator/config \
  --header 'content-type: application/json' \
  --header 'user-agent: vscode-restclient' \
  --data '{"connector.class": "io.confluent.connect.replicator.ReplicatorSourceConnector","topic.regex": "quotes","key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","header.converter": "io.confluent.connect.replicator.util.ByteArrayConverter","src.kafka.bootstrap.servers": "kafka1:29092,kafka2:29092,kafka3:29092,kafka4:29092","dest.kafka.bootstrap.servers": "broker-replicator-dst:29092","error.tolerance": "all","errors.log.enable": "true","errors.log.include.messages": "true","confluent.topic.replication.factor": 1,"provenance.header.enable": "true","topic.timestamp.type": "LogAppendTime","topic.rename.format": "replica-${topic}","tasks.max": "1"}'

  sleep 60
fi