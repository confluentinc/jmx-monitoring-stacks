# Prometheus and Grafana stack for CFK (Confluent for Kubernetes)

## Requirements

- Prometheus and Grafana deployed on Kubernetes: https://artifacthub.io/packages/helm/prometheus-community/prometheus

## How to run

- Include metrics configuration in the Confluent Platform CRDs, following [this](./cfk/confluent-platform.yaml).
- Deploy Grafana dashboards. Very similar to the ones [here](../jmxexporter-prometheus-grafana) but tweaked with Namespace and Pod variables.
