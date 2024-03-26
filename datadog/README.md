# Datadog stack

- Datadog agent version: 7.52.0-jmx

Datadog requires a [DATADOG_API_KEY](https://docs.datadoghq.com/account_management/api-app-keys/) to be added in [_start.sh_](start.sh). Datadog offers 14 day trial for new users using the link:
https://www.datadoghq.com/free-datadog-trial

## Metrics

Metrics are captured using the definition file: https://github.com/DataDog/datadog-agent/blob/main/pkg/collector/corechecks/embed/jmx/fixtures/kafka.yaml

## Dashboards

Datadog offers a predefined dashboard with Kafka metrics, named _[Kafka, Zookeeper and Kafka Consumer](https://app.datadoghq.eu/dash/integration/21/kafka-zookeeper-and-kafka-consumer-overview)_

Login to Datadog with your account after running cp-demo to visualize it.