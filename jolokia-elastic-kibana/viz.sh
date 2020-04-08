#!/bin/bash

docker-compose up -d jmx-data-poller

echo -e "\nNavigate to http://localhost:5601/app/kibana#/dashboards\n"
