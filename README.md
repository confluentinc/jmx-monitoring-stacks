# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Cloud and Confluent Platform.
While Confluent Cloud UI and Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

This project provides metrics and dashboards for:

- [Confluent Platform with Prometheus and Grafana](jmxexporter-prometheus-grafana)
- [Confluent Platform on Kubernetes with Prometheus and Grafana](jmxexporter-prometheus-grafana/cfk)
- [Confluent Platform with New Relic](jmxexporter-newrelic)
- [Confluent Platform with Metricbeat and Kibana](metricbeat-elastic-kibana)
- [Confluent Cloud with Prometheus and Grafana](ccloud-prometheus-grafana)
- [Confluent Cloud with Metricbeat and Kibana](ccloud-metricbeat-elastic-kibana)
- [Confluent Cloud with Opentelemetry and New Relic](ccloud-opentelemetry-newrelic)

## 📊 Dashboards

<p float="left">
  <img src="jmxexporter-prometheus-grafana/img/kafka-cluster-0.png" width="250" height="200" />
  <img src="jmxexporter-prometheus-grafana/img/kraft_2.png" width="250" height="200" /> 
  <img src="jmxexporter-prometheus-grafana/img/kafka-quotas.png" width="250" height="200" /> 
  <img src="jmxexporter-newrelic/img/Cluster.png" width="250" height="200" />
  <img src="jmxexporter-newrelic/img/Throughput.png" width="250" height="200" />
  <img src="metricbeat-elastic-kibana/img/kafka-overview.png" width="250" height="200" />
</p>

_and much more..._

**List of available dashboards for Confluent Platform:**

| Dashboard             |CP Prometheus and Grafana| CP New Relic | CP Metricbeat and Kibana |
|-----------------------|----|--------------|----------------------|
| Kafka Cluster         |yes| yes          | yes                  |
| Zookeeper             |yes| yes          | yes                  |
| KRaft                 |yes|              |                      |
| Schema Registry       |yes|              |yes|
| Kafka Connect         |yes|              |yes|
| ksqlDB                |yes|              |yes|
| Producer/Consumer     |yes| yes          |yes|
| Lag Exporter          |yes|           ||
| Topics                |yes|           |yes|
| Kafka Streams         |yes|           ||
| Kafka Streams RocksDB |yes|           ||
| Quotas                |yes|           ||
| TX Coordinator        |yes|           ||
| Rest Proxy            |yes|           ||
| Cluster Linking       |yes|           ||
| Oracle CDC            |yes|           ||
| Confluent RBAC        |yes|           ||
| Replicator            |yes|           ||

## ⚠️ Alerts

Alerts are available for the stacks:

 - [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana/assets/prometheus/prometheus-alerts) including alerts on broker, zookeeper and kafka connect.


# How to use with Confluent Cloud

The demo with Confluent Cloud needs a Confluent Cloud cluster and you (as a user) are required to gather some details before spinning up the Confluent Cloud monitoring solution. Please refer to this [README](ccloud-prometheus-grafana/README.md) for detailed steps to run a Confluent Cloud based sample dashboard.

# How to use with Confluent cp-ansible

To add JMX exporter configurations to cp-ansible, please refer to this [README](jmxexporter-prometheus-grafana/cp-ansible/README.md)

# How to use with Kubernetes and Confluent for Kubernetes Operator (CFK)

To add JMX exporter configurations to your Kubernetes workspace, please refer to this [README](jmxexporter-prometheus-grafana/cfk/README.md)

# How to use with cp-demo

This repo is intended to work smoothly with [Confluent cp-demo](https://github.com/confluentinc/cp-demo).

Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

NOTE: [jq](https://jqlang.github.io/jq/) is required to be installed on your machine to run the demo.

NOTE: If there is interest to test Kafka Lag Exporter (included on the monitoring stacks) make sure to use JDK 8 when running the demo, as it requires JDK8-generated certificates for the container to work (<https://github.com/lightbend/kafka-lag-exporter/issues/270>).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana), [metricbeat-elastic-kibana](metricbeat-elastic-kibana), or [jmxexporter-newrelic](jmxexporter-newrelic) and set the `MONITORING_STACK` variable accordingly.

```bash
CP_DEMO_VERSION=7.5.2-post
```

```bash
# Set one of these
MONITORING_STACK=jmxexporter-prometheus-grafana
MONITORING_STACK=metricbeat-elastic-kibana
MONITORING_STACK=jmxexporter-newrelic
```

3. Clone `cp-demo` and checkout a branch _(tested branches starts from 7.2.0-post)_.

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
(cd cp-demo && git fetch && git checkout $CP_DEMO_VERSION && git pull)
```

4. Clone `jmx-monitoring-stacks` and checkout main branch.

```bash
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout main && git pull)
```

5. Start the monitoring solution with the STACK selected. This command also starts cp-demo, you do not need to start cp-demo separately.

```bash
${MONITORING_STACK}/start.sh
```

NOTE: New Relic requires a [License Key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#overview-keys) to be added in ${MONITORING_STACK}/start.sh

6. Stop the monitoring solution. This command also stops cp-demo, you do not need to stop cp-demo separately.

```bash
${MONITORING_STACK}/stop.sh
```

# How to use with Apache Kafka client applications (producers, consumers, kafka streams applications)

For an example that showcases how to monitor Apache Kafka client applications, and steps through various failure scenarios to see how they are reflected in the provided metrics, see the [Observability for Apache Kafka® Clients to Confluent Cloud tutorial](https://docs.confluent.io/cloud/current/get-started/examples/ccloud-observability/docs/index.html).

# DEV-toolkit

To run a lightweight dev environment:

1. `cd dev-toolkit`
2. Put your new dashboards into the `grafana-wip` folder
3. `start.sh` -> It will create a minimal environment with a KRaft cluster, prometheus, grafana and a spring based java client
4. For Grafana, go to http://localhost:3000, login with _admin/grafana_
5. `stop.sh`

## Run with profiles

To add more use cases, we are leveraging the docker profiles. 

To run replicator scenario, i.e. `start.sh --profile replicator`.

## DEV-toolkit-FAQ

- What if I need more components?

More docker-compose envs will be released in the future, in the meantime you can use [Kafka Docker Composer](https://github.com/sknop/kafka-docker-composer)

- What if I need more prometheus jobs?

You can add them to the `start.sh`, i.e.

```
# ADD client monitoring to prometheus config
cat <<EOF >> assets/prometheus/prometheus-config/prometheus.yml

  - job_name: 'spring-client'
    static_configs:
      - targets: ['spring-client:9191']
        labels:
          env: "dev"
EOF
```

You can also change the prometheus configuration [here](https://github.com/confluentinc/jmx-monitoring-stacks/blob/main/jmxexporter-prometheus-grafana/assets/prometheus/prometheus-config/prometheus.yml).
