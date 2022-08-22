# Prometheus Grafana Integration with Confluent CCloud metrics (/export) endpoint 
* A Sample POC to showcase Prometheus & Grafana integration with [CCloud Metrics endpoint](https://docs.confluent.io/cloud/current/monitoring/metrics-api.html#)
* Grafana configured with Prometheus as a Datasource for  Dashboard construction.
* Prometheus Scrape config - scrapes metrics from CCloud Metrics endpoint.

## NOTE
* This demo depends on a CCloud instance available for you and you should be able to create an API Key and plugin that api key to the correct location (mentioned below). The utility could scrape the following:
  1) One or many Kafka cluster.
  2) One or many fully managed Connectors running on Confluent cloud.
  3) One or many fully managed ksqlDB cluster running on Confluent cloud.
  4) One or many Schema Registry.

## How to run

### Step 1

```
git clone https://github.com/confluentinc/jmx-monitoring-stacks
cd jmx-monitoring-stacks/ccloud-prometheus-grafana
```

### Step 2 

You will need to find some details from your CCloud Environments and feed it in this step. Please keep the following handy:
* API/Key Secret
* Inventory Information from your CCloud instance:
  * Kafka Cluster (lkc) IDs
  * ksqlDB Cluster (lksqlc) IDs
  * Connect Cluster (lcc) IDs
  * Schema Registry (lsrc) IDs

Now edit the file `./ccloud-prometheus-grafana/utils/env_variables.env` and add the above information in the respective columns:

* Update CCloud `CCLOUD_API_KEY` and `CCLOUD_API_SECRET` ( Note: Resource type= cloud Api-Key)
* Update `CCLOUD_KAFKA_LKC_ID` accepts single or multiple kafka clusters as comma-separated-string lkc-XXXX values 
  * e.g "lkc-XXXX, lkc-yyyy" or for single cluster "lkc-xxxx"
* Update `CCLOUD_CONNECT_LCC_IDS` accepts single or multiple connect clusters as comma-separated-string lcc-XXXX values
  * e.g "lcc-XXXX, lcc-yyyy" or for single cluster "lcc-xxxx"
* Update `CCLOUD_KSQL_LKSQLC_IDS` accepts single or multiple ksqlDB clusters as comma-separated-string lksqlc-XXXX values
  * e.g "lksqlc-XXXX, lksqlc-yyyy" or for single cluster "lksqlc-xxxx"
* Update `CCLOUD_SR_LSRC_IDS` accepts single or multiple Schema Registry instances as comma-separated-string lsrc-XXXX values
  * e.g "lsrc-XXXX, lsrc-yyyy" or for single instance "lsrc-xxxx"


### Step 3

* Start the CCloud export demo
``` 
./start.sh
```

### Step 4 ( select dashboard )
* Open [Grafana_Endpoint](http://localhost:3000) 
  * userid: admin
  * password: password
* Select Option to Browse Dashboards
* Open Confluent Cloud Dashboard


### Step 5
* Stop the demo
```
./stop.sh
```
## Additional Links
* [ Confluent Cloud - Monitoring/Metrics api](https://docs.confluent.io/cloud/current/monitoring/metrics-api.html)
