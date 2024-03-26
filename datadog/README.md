# Datadog stack

- Datadog agent version: 7.52.0-jmx

Datadog Agent is licensed under the Apache License 2.0
https://github.com/DataDog/datadog-agent/blob/main/LICENSE

Datadog requires a [DATADOG_API_KEY](https://docs.datadoghq.com/account_management/api-app-keys/) to be added in [_start.sh_](start.sh). Datadog offers 14 day trial for new users using the link:
https://www.datadoghq.com/free-datadog-trial

## Metrics

Metrics are captured using the definition file [kafka.yaml](assets/kafka.yaml) based on: https://github.com/DataDog/datadog-agent/blob/main/pkg/collector/corechecks/embed/jmx/fixtures/kafka.yaml

Metrics exposed:

 - broker metrics
 - producer metrics (_kafka.producer.*_)
 - consumer metrics (_kafka.consumer*_)

## Dashboards

Datadog offers a predefined dashboard with Kafka metrics, named _[Kafka, Zookeeper and Kafka Consumer](https://app.datadoghq.eu/dash/integration/21/kafka-zookeeper-and-kafka-consumer-overview)_

Login to Datadog with your account after running cp-demo to visualize it.