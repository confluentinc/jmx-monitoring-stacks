# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Platform.
While Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

- [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana)
- [metricbeat-elastic-kibana](metricbeat-elastic-kibana)
- [jolokia-elastic-kibana](jolokia-elastic-kibana)

# Caution

The examples in this repo may not be complete and are for testing purposes only.
They serve only to demonstrate how the integration works with Confluent Platform.

The Jolokia JMX Metric sets do not follow the OpenMetrics standard and we do not anticipate any updates to the package anytime soon to support that.
In purview of that, we are adding a new Prometheus Metricbeat based Elastic & Kibana setup.
We eventually plan to deprecate the jolokia-elastic-kibana module as OpenMetrics support is (hopefully) the future and metricbeat-elastic-kibana module enables us to leverage that with native code from elasticsearch.

# Run

This repo is intended to be run specifically with [cp-demo](https://github.com/confluentinc/cp-demo).
Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana), [metricbeat-elastic-kibana](metricbeat-elastic-kibana) or [jolokia-elastic-kibana](jolokia-elastic-kibana), and set the `STACK` variable accordingly.

```bash
# Set one of these
STACK=jmxexporter-prometheus-grafana
STACK=metricbeat-elastic-kibana
STACK=jolokia-elastic-kibana
```

3. Clone `cp-demo` and checkout 6.1.0-post (this has been validated only with cp-demo in the `6.1.0-post` branch).

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
(cd cp-demo && git fetch && git checkout 6.1.0-post && git pull)
```

4. Clone `jmx-monitoring-stacks` and checkout a compatible release.

```bash
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout 6.1.0-post && git pull)
```

5. Start the monitoring solution with the STACK selected. This command also starts cp-demo, you do not need to start cp-demo separately.

```bash
${STACK}/start.sh
```

6. Stop the monitoring solution. This command also stops cp-demo, you do not need to stop cp-demo separately.

```bash
${STACK}/stop.sh
```

# How to use with cp-ansible

To add JMX exporter configurations from this project into [cp-ansible](https://github.com/confluentinc/cp-ansible) add the following configurations:

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
