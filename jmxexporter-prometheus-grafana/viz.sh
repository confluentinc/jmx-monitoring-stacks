#!/bin/bash

docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nNavigate to http://localhost:3000\n"
