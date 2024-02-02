# Integration with `Confluent for Kubernetes` using the `kube-prometheus-stack`

## Demo

### Requirements

- [kind](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
- [helm](https://helm.sh/docs/intro/install/)

### Run

```
./up.sh
```

### Stop

```
./teardown.sh
```


This folder contains a Prometheus PodMonitor that will query the JMX metrics for all components of the Confluent Platform.

The Grafana dashboards need to be updated to use labels provided by Confluent for Kubernetes rather than the custom Prometheus labels for cp-demo.
Use the `cfk/update-dashboards.sh` script to create a new set of Grafana dashboards with renamed labels, then add the Grafana dashboards to Kubernetes.

Adding a Grafana dashboard as a ConfigMap:

```
kubectl create configmap grafana-zookeeper-cluster --from-file=jmxexporter-prometheus-grafana/cfk/dashboards/zookeeper-cluster.json
kubectl label configmap grafana-zookeeper-cluster grafana_dashboard=1
```

When deploying Confluent Platform with `Confluent for Kubernetes`, the default Prometheus JMX exporter configuration can be overridden with the configuration necessary for this project.

The following `metrics` configuration can be added to the Custom Resource for a Confluent Platform component:

```
spec:
  metrics:
    prometheus:
      whitelist:
        # copy the whitelistObjectNames section from the jmx-exporter yaml configuration for the component.
      blacklist:
        # copy the blacklistObjectNames section from the jmx-exporter yaml configuration for the component.
      rules:
        # copy the rules section from the jmx-exporter yaml configuration for the component.
```