# Overview

Two JMX monitoring stacks to be run in conjunction with [cp-demo](https://github.com/confluentinc/cp-demo)

* jmxexporter-prometheus-grafana
* jolokia-elastic-kibana

# Run

1. Define parameters:

* `CONFLUENT_RELEASE_TAG_OR_BRANCH`: GitHub branch to use in both conflueentinc/cp-demo and confleuntinc/jmx-monitoring-stacks (supports only `5.4.1-post` at this time)
* `STACK`: monitoring stack to demo (supports either `jmxexporter-prometheus-grafana` or `jolokia-elastic-kibana`)

```bash
CONFLUENT_RELEASE_TAG_OR_BRANCH=5.4.1-post
STACK=jolokia-elastic-kibana
```

2. Clone cp-demo and checkout the appropriate release.

```bash
[[ -d "cp-demo" ]] || git clone https://github.com/confluentinc/cp-demo.git
cd cp-demo
git fetch && git checkout ${CONFLUENT_RELEASE_TAG_OR_BRANCH} && git pull
```

3. Clone jmx-monitoring-stacks specifically into the main cp-demo folder.

```bash
# Do this from within the cp-demo directory
[[ -d "jmx-monitoring-stacks" ]] || git clone https://github.com/confluentinc/jmx-monitoring-stacks.git
(cd jmx-monitoring-stacks && git fetch && git checkout ${CONFLUENT_RELEASE_TAG_OR_BRANCH} && git pull)
```

4. Copy the docker-compose.override.yml file.

```bash
yes | cp -f jmx-monitoring-stacks/${STACK}/docker-compose.override.yml .
```

5. Run cp-demo.

```bash
./scripts/start.sh
```

6. Bring up additional containers required for the monitoring stack and visualizations.

```bash
./jmx-monitoring-stacks/${STACK}/viz.sh
```
