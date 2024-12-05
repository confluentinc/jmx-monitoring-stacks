#!/usr/bin/env bash

# build docker image with jmx exporter version 1.1.0
docker build . --no-cache --pull -t local/cp-server:7.8.0
docker save local/cp-server:7.8.0 -o cp-server.tar

# Start local k8s cluster with kind
echo "Starting local k8s cluster with kind"
kind create cluster --config ./demo/cluster.yaml
kind load image-archive cp-server.tar

# Helm repo add and update
echo "Adding and updating helm repos"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add confluentinc https://packages.confluent.io/helm
helm repo update

# Install prometheus and grafana
echo "Installing prometheus and grafana"
helm install prom prometheus-community/kube-prometheus-stack -f demo/prom.values.yaml

# Install Confluent Operator
echo "Installing Confluent Operator"
kubectl create namespace confluent
kubectl label namespace confluent monitoring=confluent
kubectl config set-context --current --namespace confluent
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes --namespace confluent

# Install podmonitor resource
kubectl apply -f pm-confluent.yaml -n confluent

# wait for the operator to be ready
echo "Waiting for the operator to be ready"
sleep 60

# Install Confluent Platform
echo "Installing Confluent Platform"
kubectl apply -f demo/confluent-platform-singlenode.yaml

# wait for the Confluent Platform to be ready
echo "Waiting for the Confluent Platform to be ready"
./update-dashboards.sh

# Create configmaps for grafana dashboards
echo "Creating configmaps for grafana dashboards"
kubectl create configmap grafana-zookeeper-cluster --from-file=dashboards/zookeeper-cluster.json
kubectl label configmap grafana-zookeeper-cluster grafana_dashboard=1
kubectl create configmap grafana-kafka-cluster --from-file=dashboards/kafka-cluster.json
kubectl label configmap grafana-kafka-cluster grafana_dashboard=1
kubectl create configmap grafana-cluster-linking --from-file=dashboards/cluster-linking.json
kubectl label configmap grafana-cluster-linking grafana_dashboard=1

# Wait resources to be ready
echo "Waiting resources to be ready"

# check if pod kafka-0 is running, otherwise sleep and retry 
while [ "$(kubectl get pods -n confluent | grep kafka-0 | awk '{print $3}')" != "Running" ]
do
    echo "Waiting for kafka-0 to be ready"
    sleep 30
done


# Forward ports
echo "Forwarding ports"
kubectl port-forward svc/prometheus-operated  9090:9090 -n default > /dev/null 2>&1 &
kubectl port-forward svc/prom-grafana 3000:80 -n default > /dev/null 2>&1 &

echo "Login to grafana at http://localhost:3000 with admin/prom-operator"
echo "Done"