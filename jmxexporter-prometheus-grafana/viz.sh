#!/bin/bash

#KAFKA_CLUSTER_ID=$(docker-compose exec zookeeper zookeeper-shell zookeeper:2181 get /cluster/id 2> /dev/null | grep \"version\" | jq -r .id)
#KAFKA_LAG_EXPORTER="User:kafkaLagExporter"
#echo "Creating role bindings for kafka lag exporter"
#docker-compose exec tools bash -c "confluent iam rolebinding create \
#    --principal $KAFKA_LAG_EXPORTER \
#    --role SystemAdmin \
#    --kafka-cluster-id $KAFKA_CLUSTER_ID"

docker-compose up -d prometheus node-exporter kafka-lag-exporter grafana

echo -e "\nView Grafana dashboards at (admin/admin) ->"
echo -e "http://localhost:3000"
