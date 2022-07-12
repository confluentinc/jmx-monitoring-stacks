import os
import grafanalib.core as G


def dashboard(ds="Prometheus", env_label="namespace", server_label="pod"):
    """
    Kafka Topics dashboard
    It includes:
    - Throughput
    - Offsets

    Structure:
    - Default sizes
    - Queries
    - Templating (variables)
    - Panel groups
    - Dashboard definition

    Dashboard is defined by a name, it includes the variables to template panels, and then adds the panels.
    Panels are grouped in Row to load only needed panels and load others on demand.

    Invariants:
    - Max width: 24
    """

    # Default sizes
    default_height = 10
    ts_width = 12
    table_width = 12
    topk = "10"

    # Queries
    by_env = env_label + '="$env"'
    by_topic = by_env + ',topic=~"$topic"'

    # Templating (variables)
    templating = G.Templating(
        list=[
            G.Template(
                name="env",
                label="Environment",
                dataSource=ds,
                query="label_values(" + env_label + ")",
            ),
            G.Template(
                name="topic",
                label="Topic",
                dataSource=ds,
                query="label_values(kafka_log_log_size{" + by_env + "}, topic)",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    # Panel groups:
    ## Throughtput:
    throughput_base = 0
    throughput_layers = 3
    throughput_panels = [
        G.RowPanel(
            title="Throughput",
            gridPos=G.GridPos(h=1, w=24, x=0, y=throughput_base),
        ),
        G.TimeSeries(
            title="Messages In/Sec",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum without(instance,pod,statefulset_kubernetes_io_pod_name) "
                    + "(rate(kafka_server_brokertopicmetrics_messagesinpersec{"
                    + by_topic
                    + "}[5m])))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 0, y=throughput_base
            ),
        ),
        G.TimeSeries(
            title="Log size",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum(kafka_log_log_size{"
                    + by_topic
                    + "}) by (topic))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 1, y=throughput_base
            ),
        ),
        G.TimeSeries(
            title="Bytes In/Sec",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum without(instance,pod,statefulset_kubernetes_io_pod_name) (rate(kafka_server_brokertopicmetrics_bytesinpersec{"
                    + by_topic
                    + "}[5m])))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 0, y=throughput_base + 1
            ),
        ),
        G.TimeSeries(
            title="Bytes Out/Sec",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum without(instance,pod,statefulset_kubernetes_io_pod_name) "
                    + "(rate(kafka_server_brokertopicmetrics_bytesoutpersec{"
                    + by_topic
                    + "}[5m])))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 1, y=throughput_base + 1
            ),
        ),
        G.TimeSeries(
            title="Produce Requests/Sec",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum(rate(kafka_server_brokertopicmetrics_totalproducerequestspersec{ "
                    + by_topic
                    + "}[5m])) by (topic))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 0, y=throughput_base + 2
            ),
        ),
        G.TimeSeries(
            title="Consumer Fetch Requests/Sec",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", sum(rate(kafka_server_brokertopicmetrics_totalfetchrequestspersec{ "
                    + by_topic
                    + "}[5m])) by (topic))",
                    legendFormat="{{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height, w=ts_width, x=ts_width * 1, y=throughput_base + 2
            ),
        ),
    ]

    offsets_txs = [
        {
          "id": "concatenate",
          "options": {
            "frameNameLabel": "id",
            "frameNameMode": "label"
          }
        },
        {
          "id": "filterFieldsByName",
          "options": {
            "include": {
              "names": [
                server_label+" 1",
                "topic 1",
                "Value #A",
                "Value #B",
                "partition 1"
              ]
            }
          }
        },
        {
          "id": "sortBy",
          "options": {
            "fields": {},
            "sort": [
              {
                "field": "partition 1"
              }
            ]
          }
        },
        {
          "id": "sortBy",
          "options": {
            "fields": {},
            "sort": [
              {
                "field": "topic 1"
              }
            ]
          }
        },
        {
          "id": "organize",
          "options": {
            "excludeByName": {},
            "indexByName": {
              "Value #A": 3,
              "Value #B": 4,
              "hostname 1": 0,
              "id": 5,
              "partition 1": 2,
              "topic 1": 1
            },
            "renameByName": {
              "Value #A": "start offset",
              "Value #B": "end offset",
              "hostname 1": "broker",
              "partition 1": "",
              "topic": "",
              "topic 1": ""
            }
          }
        }
    ]

    ## Offsets
    offsets_base = throughput_base + throughput_layers
    offsets_inner = [
        G.Table(
            title="Offsets",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_log_log_logstartoffset{" + by_topic + "}",
                    legendFormat="{{topic}}",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="kafka_log_log_logendoffset{" + by_topic + "}",
                    legendFormat="{{topic}}",
                    format="table",
                    instant=True,
                ),
            ],
            filterable=True,
            transformations=offsets_txs,
            gridPos=G.GridPos(
                h=default_height, w=table_width * 2, x=table_width * 0, y=offsets_base
            ),
        ),
    ]
    offsets_panels = [
        G.RowPanel(
            title="Offsets",
            gridPos=G.GridPos(h=1, w=24, x=0, y=offsets_base),
            collapsed=True,
            panels=offsets_inner,
        ),
    ]

    # group all panels
    panels = throughput_panels + offsets_panels

    # build dashboard
    return G.Dashboard(
        title="Kafka topics",
        description="Overview of the Kafka topics",
        tags=["confluent", "kafka"],
        inputs=[
            G.DataSourceInput(
                name="DS_PROMETHEUS",
                label="Prometheus",
                pluginId="prometheus",
                pluginName="Prometheus",
            )
        ],
        templating=templating,
        timezone="browser",
        panels=panels,
        refresh="30s",
    ).auto_panel_ids()


# main labels to customize dashboard
ds = os.environ.get("DATASOURCE", "Prometheus")
env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")

# dashboard required by grafanalib
dashboard = dashboard(ds, env_label, server_label)
