#!/usr/bin/env bash

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
      - targets: ['kafka1:1234']
        labels:
          env: "dev"
EOF

# Start the development environment
docker-compose up -d