# Prometheus Grafana Integration with Confluent CCloud metrics (/export) endpoint 
* A Sample POC to showcase  grafana/prometheus integration with  */export* (cCloud Metrics endpoint)
* Grafana configured with Prometheus as a Datasource for  Dashboard construction.
* Prometheus Scrape config - scrapes metrics data from "/export" endpoint.

## NOTE
* This demo depends on an instance of cCloud running. And it can scrape metrics for the following
1) One or many Kafka cluster, 
2) One or many fully managed Connectors running on Confluent cloud.
3) One or many fully managed ksqlDB cluster running on Confluent cloud.
4) One or many Schema Registry.
5) Principal ( authentication )

## How to run

### Step 1
* git clone Repo
* cd to "jmx-monitoring-stacks"
* export MONITORING_STACK=ccloud-openmetrics-prometheus-grafana

### Step 2 (Please refer sample file in utils directory)
* Edit/Update file ->   *./ccloud-openmetrics-prometheus-grafana/utils/env_variables.env*
* Update cCloud *"CCLOUD_API_KEY"* and *"CCLOUD_API_SECRET"* ( Note: Resource type= cloud Api-Key)
* Update *"CCLOUD_KAFKA_LKC_ID"* accepts multiple clusters as comma-seperated-string lkc-XXXX values 
         *e.g "lkc-XXXX, lkc-yyyy" or for sinlge cluster "lkc-xxxx"
* Update *CCLOUD_CONNECT_LCC_IDS* accepts multiple  lcc-XXXX values
         *e.g "lcc-XXXX, lcc-yyyy" or for sinlge cluster "lcc-xxxx"
* Update *CCLOUD_KSQL_LKSQLC_IDS* accepts single or mutiple lksqlc-XXXX values
* Update *CCLOUD_SR_LSRC_IDS"* accepts single or lsrc-XXXX values


### Step 3
* Start the cCloud export demo
 
     *${MONITORING_STACK}/start.sh*

### Step 4 ( select dashboard )
* Open Grafana ( http://localhost:3000 ) 
     userid: admin, password: admin
* Select Option to Browse Dashboards
* Open Confluent cloud Dashboard


### Step 5
* Stop the demo
     *${MONITORING_STACK}/stop.sh*

## Additional Links
* [ Confluent Cloud - Monitoring/Metrics api](https://docs.confluent.io/cloud/current/monitoring/metrics-api.html)
