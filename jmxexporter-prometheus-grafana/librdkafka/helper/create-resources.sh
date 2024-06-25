#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source ${DIR}/../helper/functions.sh

CLIENT_PRINCIPAL="User:appSA"
auth="superUser:superUser"

################################## GET KAFKA CLUSTER ID ########################
KAFKA_CLUSTER_ID=$(get_kafka_cluster_id_from_container)

################################## Create sink topic ########################
create_topic kafka1:8091 ${KAFKA_CLUSTER_ID} agg-wikipedia-page false ${auth}

################################### Client ###################################
echo "Creating role bindings for the librdkafka application"
confluent iam rbac role-binding create \
    --principal "User:appSA" \
    --role ResourceOwner \
    --resource Group:count-wikipedia-page \
    --prefix \
    --kafka-cluster-id ${KAFKA_CLUSTER_ID}

confluent iam rbac role-binding create \
    --principal "User:appSA" \
    --role ResourceOwner \
    --resource Topic:agg-wikipedia-page \
    --kafka-cluster-id ${KAFKA_CLUSTER_ID}
