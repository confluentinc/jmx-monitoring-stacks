# Integration with `cp-ansible`

To add JMX exporter configurations from this project into [Confluent cp-ansible](https://github.com/confluentinc/cp-ansible) add the following configurations:

```yaml
    zookeeper_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/zookeeper.yml
    kafka_broker_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/kafka_broker.yml
    schema_registry_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_schemaregistry.yml
    kafka_connect_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/kafka_connect.yml
    kafka_rest_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_rest.yml
    ksql_jmxexporter_config_source_path: ../../jmx-monitoring-stacks/shared-assets/jmx-exporter/confluent_ksql.yml
```

When deploying Confluent Platform with `cp-ansible`, Ansible inventories can be used to generate Prometheus configurations for static targets:

Ansible playbook: [cp-ansible/prometheus-config.yml](./cp-ansible/prometheus-config.yml)
Template: [cp-ansible/templates/prometheus.yml.j2](./cp-ansible/templates/prometheus.yml.j2)

Run the following commands providing a `cp-ansible` inventory:

```
ansible-playbook -i hosts.yml prometheus-config.yml
```

And a Prometheus configuration file should be generated:

```
scrape_configs:
  - job_name: "zookeeper"
    static_configs:
      - targets:
          - "zookeeper1:8079"
          - "zookeeper2:8079"
          - "zookeeper3:8079"
        labels:
          env: "dev"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'

  - job_name: "kafka"
    static_configs:
      - targets:
          - "kafka1:8080"
          - "kafka2:8080"
          - "kafka3:8080"
        labels:
          env: "dev"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'

  - job_name: "schemaregistry"
    static_configs:
      - targets:
          - "schemaregistry1:8078"
          - "schemaregistry2:8078"
        labels:
          env: "dev"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'

  - job_name: "connect"
    static_configs:
      - targets:
          - "connect1:8077"
          - "connect2:8077"
        labels:
          env: "dev"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'

  - job_name: "ksqldb"
    static_configs:
      - targets:
          - "ksqldbserver1:8077"
          - "ksqldbserver2:8077"
        labels:
          env: "dev"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(:[0-9]+)?'
        replacement: '${1}'
```

This configuration can be added to the Prometheus config file.
Once Prometheus is restarted with this configuration, targets will be scrapped.