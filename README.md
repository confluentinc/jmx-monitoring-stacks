# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Platform.
While Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

- [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana)
- [jmxexporter-elastic-kibana](jmxexporter-elastic-kibana)
- [jolokia-elastic-kibana](jolokia-elastic-kibana)

# Caution

The examples in this repo may not be complete and are for testing purposes only.
They serve only to demonstrate how the integration works with Confluent Platform.

The Jolokia JMX Metric sets do not follow the OpenMetrics standard and we do not anticipate any updates to the package anytime soon to support that.
In purview of that, we are adding a new Prometheus Metricbeat based Elastic & Kibana setup.
We eventually plan to deprecate the jolokia-elastic-kibana module as OpenMetrics support is the future and jmxexporter-elastic-kibana module enables us to leverage that with native code from elasticsearch.

# Run

This repo is intended to be run specifically with [cp-demo](https://github.com/confluentinc/cp-demo).
Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana), [jmxexporter-elastic-kibana](jmxexporter-elastic-kibana) or [jolokia-elastic-kibana](jolokia-elastic-kibana), and set the `STACK` variable accordingly.

```bash
# Set one of these
STACK=jmxexporter-prometheus-grafana
STACK=jmxexporter-elastic-kibana
STACK=jolokia-elastic-kibana
```

3. Clone `cp-demo` and checkout 6.0.0-post (this has been validated only with cp-demo in the `6.0.0-post` branch).

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
(cd cp-demo && git fetch && git checkout 6.0.0-post && git pull)
```

4. Clone `jmx-monitoring-stacks` and checkout a compatible release.

```bash
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout 6.0.0-post && git pull)
```

5. Start the monitoring solution with the STACK selected. This command also starts cp-demo, you do not need to start cp-demo separately.

```bash
${STACK}/start.sh
```

6. Stop the monitoring solution. This command also stops cp-demo, you do not need to stop cp-demo separately.

```bash
${STACK}/stop.sh
```
