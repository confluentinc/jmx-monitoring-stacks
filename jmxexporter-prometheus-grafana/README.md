# Prometheus and Grafana stack

List of provided dashboards:
 - [Confluent Platform overview](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#confluent-platform-overview)
 - [Zookeeper cluster](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#zookeeper-cluster)
 - [Kafka cluster](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-cluster)
 - [Kafka topics](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-topics)
 - [Kafka Clients](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-clients)
 - [Kafka quotas](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-quotas)
 - [Schema Registry cluster](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#schema-registry-cluster)
 - [Kafka Connect cluster](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-connect-cluster)
 - [ksqlDB cluster](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#ksqldb-cluster)
 - [Kafka streams](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-streams)
 - [Kafka streams RocksDB](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-streams-rocksdb)
 - [Oracle CDC source Connector](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#oracle-cdc-source-connector)
 - [Kafka lag exporter](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-lag-exporter)
 - [Kafka transaction coordinator](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/README.md#kafka-transaction-coordinator)
 - Cluster Linking

### Confluent Platform overview

![Confluent Platform overview](img/confluent-platform-overview.png)

### Zookeeper cluster

![Zookeeper cluster dashboard](img/zookeeper-cluster.png)

### Kafka cluster

![Kafka cluster dashboard 0](img/kafka-cluster-0.png)
![Kafka cluster dashboard 1](img/kafka-cluster-1.png)

### Kafka topics

![Kafka topics](img/kafka-topics.png)

### Kafka Clients

![Kafka Producer](img/kafka-producer.png)

![Kafka Consumer](img/kafka-consumer.png)

### Kafka quotas

For Kafka to output quota metrics, at least one quota configuration is necessary.

A quota can be configured from the cp-demo folder using docker-compose:
```bash
docker-compose exec kafka1 kafka-configs --bootstrap-server kafka1:12091 --alter --add-config 'producer_byte_rate=10000,consumer_byte_rate=30000,request_percentage=0.2' --entity-type users --entity-name unknown --entity-type clients --entity-name unknown
```

![Kafka quotas](img/kafka-quotas.png)

### Schema Registry cluster

![Schema Registry cluster](img/schema-registry-cluster.png)

### Kafka Connect cluster

![Kafka Connect cluster dashboard 0](img/kafka-connect-cluster-0.png)
![Kafka Connect cluster dashboard 1](img/kafka-connect-cluster-1.png)

### ksqlDB cluster

![ksqlDB cluster dashboard 0](img/ksqldb-cluster-0.png)
![ksqlDB cluster dashboard 1](img/ksqldb-cluster-1.png)

### Kafka streams

![Kafka streams dashboard 0](img/kafka-streams.png)

### Kafka streams RocksDB 

![kafkastreams-rocksdb 0](img/kafkastreams-rocksdb.png)

### Oracle CDC source Connector

To test run [playground example](https://github.com/vdesabou/kafka-docker-playground/tree/master/connect/connect-cdc-oracle19-source) using 
```bash
--enable-jmx-grafana
```
![oraclecdc](img/oraclecdc.jpg)

### Kafka Lag Exporter

![kafkalagexporter](img/kafka-lag-exporter.png)

### Kafka Transaction Coordinator

![kafkalagexporter](img/kafka-transaction-coordinator.png)