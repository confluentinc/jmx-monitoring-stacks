import os
import grafanalib.core as G


def dashboard(env_label="namespace", server_label="pod"):
    default_height = 5
    stat_width = 4
    ts_width = 8

    templating = G.Templating(
        list=[
            G.Template(
                name="env",
                label="Environment",
                dataSource="Prometheus",
                query="label_values(" + env_label + ")",
            ),
            G.Template(
                name="zk_server",
                label="Server",
                dataSource="Prometheus",
                query="label_values(zookeeper_outstandingrequests{"
                + env_label
                + '="$env"}, '
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="quantile",
                label="Quantile",
                dataSource="Prometheus",
                query="label_values(kafka_server_zookeeperclientmetrics_zookeeperrequestlatencyms{"
                + env_label
                + '="$env"}, quantile)',
            ),
        ]
    )

    healthcheck_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="ZK: Quorum Size",
            description="""Quorum Size of Zookeeper ensemble.
            Count Zookeeper servers with quorum size metric.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="count(zookeeper_status_quorumsize{" + env_label + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="red"),
                G.Threshold(index=1, value=2.0, color="yellow"),
                G.Threshold(index=2, value=3.0, color="green"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=0),
        ),
        G.Stat(
            title="ZK: ZNodes (avg.)",
            description="""Average size of ZNodes in the cluster.
            Getting the node count per server, and averaging the node count.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="avg(zookeeper_inmemorydatatree_nodecount{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=0),
        ),
        G.Stat(
            title="ZK: Connections used",
            description="""Sum of the number of alive connections per servers divided by the maximum number of client connections allowed per host.
            If the percentage is higher than 60%, then Zookeeper should be scaled and/or the Zookeeper clients should be investigated to find the reason for high number of connections opened.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="zookeeper_numaliveconnections{"
                    + env_label
                    + '="$env"} / zookeeper_maxclientcnxnsperhost{'
                    + env_label
                    + '="$env"}',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=0.6, color="yellow"),
                G.Threshold(index=2, value=0.8, color="red"),
            ],
            format="percentunit",
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=0),
        ),
        G.Stat(
            title="ZK: Sum of watchers",
            description="""Sum of client watchers subscribed to changes on the ZNodes.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum(zookeeper_inmemorydatatree_watchcount{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=0),
        ),
        G.TimeSeries(
            title="ZK: Outstanding Requests",
            description="""Number of requests waiting for processing (queued).
            If the number of outstanding requests grows higher than 10, then the Zookeeper hosts should be checked.
            It could mean that there is not enough resources to cope with the number of requests.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="zookeeper_outstandingrequests{" + env_label + '="$env"}',
                    legendFormat="{{"
                    + server_label
                    + "}} ({{server_id}}:{{member_type}})",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "last"],
            legendPlacement="right",
            gridPos=G.GridPos(h=default_height, w=ts_width, x=stat_width * 4, y=0),
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="yellow"),
                G.Threshold(index=2, value=10.0, color="red"),
            ],
        ),
    ]

    system_panels = [
        G.RowPanel(
            title="System",
            gridPos=G.GridPos(h=1, w=24, x=0, y=1),
        ),
        G.TimeSeries(
            title="CPU usage",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="irate(process_cpu_seconds_total{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$zk_server"}[5m])',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=1),
        ),
        G.TimeSeries(
            title="Memory usage",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum without(area)(jvm_memory_bytes_used{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '="$zk_server"})',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=1),
        ),
        G.TimeSeries(
            title="GC collection",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum without(gc)(irate(jvm_gc_collection_seconds_sum{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '="$zk_server"}[5m]))',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=1),
        ),
    ]

    # TODO: validate if latency metrics make sense.
    # Values are high-watermark of the metric and multiplied by tick-time to represent milliseconds.
    latency_inner = [
        G.TimeSeries(
            title="ZK: Request Latency (Minimum)",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="zookeeper_minrequestlatency{"
                    + env_label
                    + '="$env"} * zookeeper_ticktime',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=2),
        ),
        G.TimeSeries(
            title="ZK: Request Latency (Average)",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="zookeeper_avgrequestlatency{"
                    + env_label
                    + '="$env"} * zookeeper_ticktime',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=2),
        ),
        G.TimeSeries(
            title="ZK: Request Latency (Maximum)",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="zookeeper_maxrequestlatency{"
                    + env_label
                    + '="$env"} * zookeeper_ticktime',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=2),
        ),
    ]
    latency_panels = [
        G.RowPanel(
            title="Server Latency",
            gridPos=G.GridPos(h=1, w=24, x=0, y=2),
            collapsed=True,
            panels=latency_inner,
        ),
    ]

    kafka_base = 2 + 1
    kafka_inner = [
        G.TimeSeries(
            title="Kafka: Request Latency",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_server_zookeeperclientmetrics_zookeeperrequestlatencyms{"
                    + env_label
                    + '="$env",quantile=~"$quantile"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=kafka_base
            ),
        ),
        G.TimeSeries(
            title="Kafka: Sync Connections/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_server_sessionexpirelistener_zookeepersyncconnectspersec{"
                    + env_label
                    + '="$env"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=kafka_base
            ),
        ),
        G.TimeSeries(
            title="Kafka: Expired Connections/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_server_sessionexpirelistener_zookeeperexpirespersec{"
                    + env_label
                    + '="$env"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=kafka_base
            ),
        ),
        G.TimeSeries(
            title="Kafka: Disconnected Connections/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_server_sessionexpirelistener_zookeeperdisconnectspersec{"
                    + env_label
                    + '="$env"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=kafka_base + 1
            ),
        ),
        G.TimeSeries(
            title="Kafka: Auth Failures on Connections/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_server_sessionexpirelistener_zookeeperauthfailurespersec{"
                    + env_label
                    + '="$env"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=kafka_base + 1
            ),
        ),
    ]
    kafka_panels = [
        G.RowPanel(
            title="Client Latency (Kafka)",
            gridPos=G.GridPos(h=1, w=24, x=0, y=kafka_base),
            collapsed=True,
            panels=kafka_inner,
        ),
    ]

    panels = healthcheck_panels + system_panels + latency_panels + kafka_panels

    return G.Dashboard(
        title="Zookeeper cluster - v2",
        description="Overview of the Zookeeper cluster",
        tags=["confluent", "kafka", "zookeeper"],
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


env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
dashboard = dashboard(env_label, server_label)
