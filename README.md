# Overview

Two JMX monitoring stacks to be run specifically in conjunction with [cp-demo](https://github.com/confluentinc/cp-demo)

* jmxexporter-prometheus-grafana
* jolokia-elastic-kibana


# Run

1. Define parameters

```bash
CONFLUENT_RELEASE_TAG_OR_BRANCH=5.4.1-post
STACK=jolokia-elastic-kibana
```

2. Clone cp-demo and checkout the appropriate release

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
cd cp-demo
git fetch && git checkout ${CONFLUENT_RELEASE_TAG_OR_BRANCH} && git pull
```

3. Clone jmx-monitoring-stacks specifically into the main cp-demo folder

```bash
# Do this from with the cp-demo directory
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout ${CONFLUENT_RELEASE_TAG_OR_BRANCH} && git pull)
```

4. Copy the docker-compose.override.yml file

```bash
yes | cp -f jmx-monitoring-stacks/${STACK}/docker-compose.override.yml .
```

5. Run cp-demo

```bash
./scripts/start.sh
```
