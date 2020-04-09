#!/bin/bash

docker-compose up -d jmx-data-poller

echo -e "\nView Kibana dashboards at ->"
echo -e "http://localhost:5601/app/kibana#/dashboards\n"
