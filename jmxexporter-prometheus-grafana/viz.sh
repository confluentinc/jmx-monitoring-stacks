#!/bin/bash

docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nView Grafana dashboards at (admin/admin) ->"
echo -e "http://localhost:3000"
