# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Platform.
While Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

* [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana)
* [jolokia-elastic-kibana](jolokia-elastic-kibana)

# Caution

The examples in this repo may not be complete and are for testing purposes only.
They serve only to demonstrate how the integration works with Confluent Platform.

# Run

This repo is intended to be run specifically with [cp-demo](https://github.com/confluentinc/cp-demo).
Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana) or [jolokia-elastic-kibana](jolokia-elastic-kibana), and set the `STACK` variable accordingly.

```bash
# Set one of these
STACK=jmxexporter-prometheus-grafana
STACK=jolokia-elastic-kibana
```

3. Clone `cp-demo` and checkout 5.5.0-post (this has been validated only with cp-demo in the `5.5.0-post` branch).

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
(cd cp-demo && git fetch && git checkout 5.5.0-post && git pull)
```

4. Clone `jmx-monitoring-stacks` and checkout a compatible release.

```bash
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout 5.5.0-post && git pull)
```

5. Start the monitoring solution with the STACK selected. Note that this also starts cp-demo, you do not need to start cp-demo separately.

```bash
${STACK}/start.sh
```

6. Stop the monitoring solution.

```bash
${STACK}/stop.sh
```
