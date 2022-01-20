# Overview

This repo demonstrates examples of JMX monitoring stacks that can monitor Confluent Platform.
While Confluent Control Center provides an opinionated view of Apache Kafka monitoring, JMX monitoring stacks serve a larger purpose to our users, allowing them to setup monitoring across multiple parts of their organization, many outside of Kafka, and to have a single pane of glass.

- [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana)
- [metricbeat-elastic-kibana](metricbeat-elastic-kibana)
- [jolokia-elastic-kibana](jolokia-elastic-kibana)
- [ccloud-openmetrics-prometheus-grafana](ccloud-openmetrics-prometheus-grafana)
# Caution

The examples in this repo may not be complete and are for testing purposes only.
They serve only to demonstrate how the integration works with Confluent Platform.

The Jolokia JMX Metric sets do not follow the OpenMetrics standard and we do not anticipate any updates to the package anytime soon to support that.
In purview of that, we are adding a new Prometheus Metricbeat based Elastic & Kibana setup.
We eventually plan to deprecate the jolokia-elastic-kibana module as OpenMetrics support is (hopefully) the future and metricbeat-elastic-kibana module enables us to leverage that with native code from elasticsearch.


# How to run with cp-demo

This repo is intended to be run specifically with [cp-demo](https://github.com/confluentinc/cp-demo).
Make sure you have enough system resources on the local host to run this.
Verify in the advanced Docker preferences settings that the memory available to Docker is at least 8 GB (default is 2 GB).

NOTE: If there is interest to test Kafka Lag Exporter (included on the monitoring stacks) make sure to use JDK 8 when running the demo, as it requires JDK8-generated certificates for the container to work (<https://github.com/lightbend/kafka-lag-exporter/issues/270>).

1. Ensure that cp-demo is not already running on the local host.

2. Decide which monitoring stack to demo: either [jmxexporter-prometheus-grafana](jmxexporter-prometheus-grafana), [metricbeat-elastic-kibana](metricbeat-elastic-kibana) or [jolokia-elastic-kibana](jolokia-elastic-kibana), and set the `MONITORING_STACK` variable accordingly.

```bash
# Set one of these
MONITORING_STACK=jmxexporter-prometheus-grafana
MONITORING_STACK=metricbeat-elastic-kibana
MONITORING_STACK=jolokia-elastic-kibana
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
${MONITORING_STACK}/start.sh
```

6. Stop the monitoring solution. This command also stops cp-demo, you do not need to stop cp-demo separately.

```bash
${MONITORING_STACK}/stop.sh
```
# How to run with cCloud "/export" endpoint (openMetrics endpoint)

For a sample demo of generating grafana/prometheus  connecting to cCloud. Please follow the step below
### Step 1.  
    clone git repo
### Step 2. Set environment variables
    update the file in ccloud-openmetrics-prometheus-grafana/utils/env_variables.env
    Details about environment variables are given below
### Step 3.  Start monitoring solution
    Run script  ( ${MONITORING_STACK}/start.sh )
### Step 4.  Stop monitoring solution
    Run script  ( ${MONITORING_STACK}/stop.sh )

## Additional details for cCloud example:

If you have a cCloud instance running , with a cluster with few topics, a managed connector or a managed ksqlDB applications. Gather the ids of each of the resources  and follow the steps as mentioned above  to integrate grafana & prometheus with cCloud "/export" endpoint. 

*NOTE : This example depends on cCloud cluster & other managed clusters in confluent cloud. This example does not spin up a cCloud instance automatically.*

1. Following env variable to be set
```bash
# Mandatory env variables
export MONITORING_STACK=ccloud-openmetrics-prometheus-grafana
export CCLOUD_API_KEY=<CCLOUD-API-KEY> # Resource group cloud
export CCLOUD_API_SECRET=<CCLOUD-API-secret>
export CCLOUD_KAFKA_LKC_IDS=<Kafka-cluster-ids>  #One or many seperated by ","

#Optional resource ids to set based on scraping requirement
export CCLOUD_CONNECT_LCC_IDS=<ccloud-connect-cluster-ids>  #One or many seperated by ","
export CCLOUD_KSQL_LKSQLC_IDS=<ccloud-ksql-cluster-ids>  #One or many seperated by ","
export CCLOUD_SR_LSRC_IDS=<ccloud-SR-cluster-ids>  #One or many seperated by ","
```
2. Spin a cCloud instance with (SR, Kafka Cluster, fully managed connectors, fully managed ksqlDB)

3. Start & stop command

```bash
${MONITORING_STACK}/start.sh
${MONITORING_STACK}/stop.sh
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
