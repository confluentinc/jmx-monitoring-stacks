# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Cloud and Confluent Platform.
While Confluent Cloud UI and Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

- [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana)
- [metricbeat-elastic-kibana](metricbeat-elastic-kibana)
- [ccloud-prometheus-grafana](ccloud-prometheus-grafana)
- [ccloud-metricbeat-elastic-kibana](ccloud-metricbeat-elastic-kibana)
- [jmxexporter-newrelic](jmxexporter-newrelic)

# Caution

The examples in this repo may not be complete and are for testing purposes only.
They serve only to demonstrate how the integration works with Confluent Cloud and Confluent Platform.

# How to run with cp-demo

This repo is intended to be run specifically with [Confluent cp-demo](https://github.com/confluentinc/cp-demo).
Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

NOTE: If there is interest to test Kafka Lag Exporter (included on the monitoring stacks) make sure to use JDK 8 when running the demo, as it requires JDK8-generated certificates for the container to work (<https://github.com/lightbend/kafka-lag-exporter/issues/270>).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana), [metricbeat-elastic-kibana](metricbeat-elastic-kibana), or [jmxexporter-newrelic](jmxexporter-newrelic) and set the `MONITORING_STACK` variable accordingly.

```bash
# Set one of these
MONITORING_STACK=jmxexporter-prometheus-grafana
MONITORING_STACK=metricbeat-elastic-kibana
MONITORING_STACK=jmxexporter-newrelic
```

3. Clone `cp-demo` and checkout 7.2.0-post (this has been validated only with cp-demo in the `7.2.0-post` branch).

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
(cd cp-demo && git fetch && git checkout 7.2.0-post && git pull)
```

4. Clone `jmx-monitoring-stacks` and checkout a compatible release.

```bash
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout 7.2-post && git pull)
```

5. Start the monitoring solution with the STACK selected. This command also starts cp-demo, you do not need to start cp-demo separately.

```bash
${MONITORING_STACK}/start.sh
```

**_NOTE:_**  New Relic requires a [License Key](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#overview-keys) in the command - ${MONITORING_STACK}/start.sh e4d7b76e0ff30730bb

6. Stop the monitoring solution. This command also stops cp-demo, you do not need to stop cp-demo separately.

```bash
${MONITORING_STACK}/stop.sh
```
# How to run with CCloud "/export" endpoint (openMetrics endpoint)

The demo with CCloud needs a CCloud Instance running and you (as a user) are required to gather some details before spinning up the CCloud monitoring solution. Please refer to this [README](ccloud-prometheus-grafana/README.md) for detailed steps to run a CCloud based sample dashboard.

# How to use with cp-ansible

To add JMX exporter configurations from this project into [Confluent cp-ansible](https://github.com/confluentinc/cp-ansible) add the following configurations:

```yaml
    zookeeper_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/zookeeper.yml
    kafka_broker_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/kafka_broker.yml
    schema_registry_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_schemaregistry.yml
    kafka_connect_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/kafka_connect.yml
    kafka_rest_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_rest.yml
    ksql_jmxexporter_config_source_path: ../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_ksql.yml
```

Add and execute the Ansible template task [here](jmxexporter-prometheus-grafana/cp-ansible/prometheus-config.yml) to generate the Prometheus configuration for your Ansible inventory.

# See Also

For an example that showcases how to monitor Apache Kafka client applications, and steps through various failure scenarios to see how they are reflected in the provided metrics, see the [Observability for Apache Kafka® Clients to Confluent Cloud tutorial](https://docs.confluent.io/platform/current/tutorials/examples/ccloud-observability/docs/observability-overview.html).
