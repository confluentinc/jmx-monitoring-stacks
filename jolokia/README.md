# Jolokia Agent

This demo provides the installation of a Jolokia Agent for each component of Confluent Platform.

Example of how to read a value for a MBean with Jolokia:

```bash
curl http://localhost:8778/jolokia/read/java.lang:type\=Memory/HeapMemoryUsage | jq

{
  "request": {
    "mbean": "java.lang:type=Memory",
    "attribute": "HeapMemoryUsage",
    "type": "read"
  },
  "value": {
    "init": 1073741824,
    "committed": 1073741824,
    "max": 1073741824,
    "used": 691734528
  },
  "status": 200,
  "timestamp": 1705933656
}
```

Jolokia allows you to request a list of MBeans and retrieve the value for a specific attribute with a single HTTP POST, for example:

```bash 
curl -X POST --data @request.json "http://localhost:8778/jolokia/read?includeStackTrace=false" | jq

[
  {
    "request": {
      "mbean": "kafka.server:name=ControlPlaneRequestHandlerAvgIdlePercent,type=KafkaRequestHandlerPool",
      "attribute": "FifteenMinuteRate",
      "type": "read"
    },
    "value": 0.0,
    "status": 200,
    "timestamp": 1711541027
  },
  {
    "request": {
      "mbean": "kafka.server:name=RequestHandlerAvgIdlePercent,type=KafkaRequestHandlerPool",
      "attribute": "FifteenMinuteRate",
      "type": "read"
    },
    "value": 0.9505627028636324,
    "status": 200,
    "timestamp": 1711541027
  }
]
```

List of Jolokia endpoint per component:

- zookeeper:
```bash
curl http://localhost:8777/jolokia/list | jq
```

- kafka1: 
```bash
curl http://localhost:8778/jolokia/list | jq
```

- kafka2: 
```bash
curl http://localhost:8779/jolokia/list | jq
```

- connect:
```bash
curl http://localhost:8781/jolokia/list | jq
```

- schema registry:
```bash
curl http://localhost:8782/jolokia/list | jq
```

- ksql:
```bash
curl http://localhost:8783/jolokia/list | jq
```

- rest proxy:
```bash
curl http://localhost:8784/jolokia/list | jq
```