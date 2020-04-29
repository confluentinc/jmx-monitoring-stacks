#!/bin/bash

. ../helper/configure_cp_demo.sh

echo -e "Launch CP - demo"
(cd $CP_DEMO_HOME && ./scripts/start.sh)

echo -e "Starting jmx-data-poller"
docker-compose up -d jmx-data-poller

echo -e "\nView Kibana dashboards at ->"
echo -e "http://localhost:5601/app/kibana#/dashboards\n"
