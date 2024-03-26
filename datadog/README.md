# Datadog stack

- Datadog agent version: 7.52.0-jmx

Datadog Agent is licensed under the Apache License 2.0
https://github.com/DataDog/datadog-agent/blob/main/LICENSE

Datadog requires a [DATADOG_API_KEY](https://docs.datadoghq.com/account_management/api-app-keys/) and [DATADOG_SITE](https://docs.datadoghq.com/getting_started/site/) to be added in [_start.sh_](start.sh). Datadog offers 14 day trial for new users.

## Metrics

Metrics are captured using the definition file [kafka.yaml](assets/kafka.yaml) based on: https://github.com/DataDog/datadog-agent/blob/main/pkg/collector/corechecks/embed/jmx/fixtures/kafka.yaml

Metrics exposed:

 - broker metrics
 - producer metrics (_kafka.producer.*_)
 - consumer metrics (_kafka.consumer*_)

## Dashboards

Datadog offers a predefined dashboard with Kafka metrics, named _[Kafka, Zookeeper and Kafka Consumer](https://app.datadoghq.eu/dash/integration/21/kafka-zookeeper-and-kafka-consumer-overview)_

Login to Datadog with your account after running cp-demo to visualize it.
Depending on your region use:
 - US1	https://app.datadoghq.com	datadoghq.com	US
 - US3	https://us3.datadoghq.com	us3.datadoghq.com	US
 - US5	https://us5.datadoghq.com	us5.datadoghq.com	US
 - EU1	https://app.datadoghq.eu	datadoghq.eu	EU
 - US1-FED	https://app.ddog-gov.com	ddog-gov.com	US
 - AP1	https://ap1.datadoghq.com	ap1.datadoghq.com	Japan

## Confluent Platform Datadog integration

Datadog offers a specific integration with Confluent Platform _(no predefined dashboards)_. To install the integration follow thew instructions at:
https://docs.datadoghq.com/integrations/confluent_platform/