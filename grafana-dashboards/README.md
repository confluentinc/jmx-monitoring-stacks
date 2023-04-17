# Grafana dashboards for Confluent Platform

## Dashboards

- Confluent Platform overview: main metrics from all Confluent components.
- Kafka Cluster: Kafka cluster heath and performance metrics.
- Kafka Topics: Kafka topics throughput metrics.
- Schema Registry Cluster: Servers and subjects/schemas metrics.
- Kafka Connect Cluster: Connect workers and connectors metrics.
- ksqlDB Cluster: Servers and queries metrics.
- Kafka Producer: Kafka producer client metrics.
- Kafka Consumer: Kafka consumer client metrics.
- Kafka Quotas: Kafka quotas and throttling metrics.

## How to build

Install `grafanalib` library:

```shell
pip3 install grafanalib
```

Run makefile:

```shell
make
```

This execution generates the grafana dashboard JSON files on directories `default/` for Docker/VM-based deployments and `cfk/` for Confluent-for-Kubernetes-based deployments.

## How to use

Grafana dashboards expect the following labels:

- Environment:
  - Default: `env`
  - CFK: `namespace`
- Server label:
  - Default: `hostname`
  - CFK: `pod`
- Cluster labels:
  - Connect:
    - Default: `kafka_connect_cluster_id`
    - CFK: `app`
  - ksqlDB:
    - Default: `ksqldb_cluster_id`
    - CFK: `app`

