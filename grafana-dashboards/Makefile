all: 
	$(MAKE) def
	$(MAKE) cfk

def: OUTPUT_DIR=default
def: export ENV_LABEL=env
def: export SERVER_LABEL=hostname
def: export KSQLDB_CLUSTER_LABEL=ksqldb_cluster_id
def: export CONNECT_CLUSTER_LABEL=kafka_connect_cluster_id
.PHONY: def
def: dashboards

OUTPUT_DIR=default
dashboards:
	@mkdir -p $(OUTPUT_DIR)
	@generate-dashboard confluent-platform.py -o $(OUTPUT_DIR)/confluent-platform.json 
	@generate-dashboard zookeeper-cluster.py -o $(OUTPUT_DIR)/zookeeper-cluster.json
	@generate-dashboard kafka-cluster.py -o $(OUTPUT_DIR)/kafka-cluster.json
	@generate-dashboard kafka-topics.py -o $(OUTPUT_DIR)/kafka-topics.json
	@generate-dashboard schema-registry-cluster.py -o $(OUTPUT_DIR)/schema-registry-cluster.json
	@generate-dashboard kafka-connect-cluster.py -o $(OUTPUT_DIR)/kafka-connect-cluster.json
	@generate-dashboard ksqldb-cluster.py	-o $(OUTPUT_DIR)/ksqldb-cluster.json
	@generate-dashboard kafka-producer.py	-o $(OUTPUT_DIR)/kafka-producer.json
	@generate-dashboard kafka-consumer.py	-o $(OUTPUT_DIR)/kafka-consumer.json
	@generate-dashboard kafka-quotas.py	-o $(OUTPUT_DIR)/kafka-quotas.json

cfk: OUTPUT_DIR=cfk
cfk: export ENV_LABEL=namespace
cfk: export SERVER_LABEL=pod
cfk: export KSQLDB_CLUSTER_LABEL=app
cfk: export CONNECT_CLUSTER_LABEL=app
.PHONY: cfk
cfk: dashboards
