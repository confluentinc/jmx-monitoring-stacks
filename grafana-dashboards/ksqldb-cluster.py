import os
import grafanalib.core as G


def dashboard(
    ds="Prometheus",
    env_label="namespace",
    server_label="pod",
    ksqldb_cluster_label="app",
):
    """
    ksqlDB cluster dashboard
    It includes:
    - Cluster overview
    - System resources
    - Query Performance
    - State Stores

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
    default_height = 5
    stat_width = 4
    ts_width = 8

    # Queries
    by_env = env_label + '="$env"'
    by_cluster = by_env + "," + ksqldb_cluster_label + '="$ksqldb_cluster"'
    by_server = by_cluster + "," + server_label + '=~"$ksqldb_server"'
    by_thread = by_server + 'thread_id=~".+$ksqldb_cluster_id.+"'

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
                name="ksqldb_cluster",
                label="ksqlDB cluster",
                dataSource=ds,
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + by_env
                + "},"
                + ksqldb_cluster_label
                + ")",
            ),
            G.Template(
                name="ksqldb_cluster_id",
                label="ksqlDB cluster ID",
                dataSource=ds,
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + by_env
                + "},ksql_cluster)",
                hide=2,  # true
            ),
            G.Template(
                name="ksqldb_server",
                label="ksqlDB server",
                dataSource=ds,
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + by_cluster
                + "}, "
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    # Panel groups
    ## Cluster overview:
    ### When updating descriptions on these panels, also update descriptions in confluent-platform.py
    overview_base = 0
    overview_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=overview_base),
        ),

        # First layer
        G.Stat(
            title="ksqlDB: Online Servers",
            description="""ksqlDB online instances returning metrics.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(ksql_ksql_engine_query_stats_num_active_queries{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 0, y=overview_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Active Queries",
            description="""Number of active queries deployed in the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_num_active_queries{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 1, y=overview_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Running Queries",
            description="""Number of running queries deployed in the cluster.
            Ideally, this number should be equal to the number of active queries as queries should be running.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_running_queries{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="green"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 2, y=overview_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Rebalancing Queries",
            description="""Number of queries rebalancing in the cluster.
            Ideally, this number should be equal zero, or return to zero in a short period (e.g. 1 minute).
            It's recommended to alert if the number of rebalancing queries stay higher than 0 for a longer period of time.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_rebalancing_queries{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="yellow"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 3, y=overview_base
            ),
        ),
        G.Stat(
            title="Connect: Sum of Queries Failed",
            description="""Number of queries failed in the cluster.
            Ideally, this number should be equal zero.
            It's recommended to alert if the number of queries failed is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="avg(ksql_ksql_engine_query_stats_error_queries{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 4, y=overview_base
            ),
        ),

        # Second layer
        G.TimeSeries(
            title="Cluster Liveness",
            description="A metric with constant value 1 indicating the server is up and emitting metrics.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_liveness_indicator{"
                    + by_cluster
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=0, y=overview_base + 1),
        ),
        G.TimeSeries(
            title="Messages consumed/sec",
            description="The number of messages consumed per second across all queries.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_messages_consumed_per_sec{"
                    + by_cluster
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=overview_base + 1
            ),
        ),
        G.TimeSeries(
            title="Messages produced/sec",
            description="The number of messages produced per second across all queries.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_messages_produced_per_sec{"
                    + by_cluster
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=overview_base + 1
            ),
        ),
    ]

    ## System resources:
    ### When updating descriptions on these panels, also update descriptions in other cluster dashboards
    system_base = overview_base + 2
    system_panels = [
        G.RowPanel(
            title="System",
            gridPos=G.GridPos(h=1, w=24, x=0, y=system_base),
        ),
        G.TimeSeries(
            title="CPU usage",
            description="""Rate of CPU seconds used by the Java process.
            100% usage represents one core. 
            If there are multiple cores, the total capacity should be 100% * number_cores.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="irate(process_cpu_seconds_total{" + by_server + "}[5m])",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=system_base
            ),
        ),
        G.TimeSeries(
            title="Memory usage",
            description="""Sum of JVM memory used, without including areas (e.g. heap size).""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without(area)(jvm_memory_bytes_used{" + by_server + "})",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=system_base
            ),
        ),
        G.TimeSeries(
            title="GC collection",
            description="""Sum of seconds used by Garbage Collection.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without(gc)(irate(jvm_gc_collection_seconds_sum{"
                    + by_server
                    + "}[5m]))",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=system_base
            ),
        ),
    ]

    ## Query performance
    queries_base = system_base + 1
    queries_inner = [
        G.TimeSeries(
            title="Poll Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_poll_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=queries_base
            ),
        ),
        G.TimeSeries(
            title="Poll Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_poll_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=queries_base
            ),
        ),
        G.TimeSeries(
            title="Process Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_process_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=queries_base + 1
            ),
        ),
        G.TimeSeries(
            title="Process Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_process_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=queries_base + 1
            ),
        ),
        G.TimeSeries(
            title="Commit Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_commit_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=queries_base + 2
            ),
        ),
        G.TimeSeries(
            title="Commit Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_commit_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=queries_base + 2
            ),
        ),
        G.TimeSeries(
            title="Punctuate Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_punctuate_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=queries_base + 3
            ),
        ),
        G.TimeSeries(
            title="Punctuate Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_punctuate_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=queries_base + 3
            ),
        ),
    ]
    queries_panels = [
        G.RowPanel(
            title="Queries Performance",
            gridPos=G.GridPos(h=1, w=24, x=0, y=queries_base),
            collapsed=True,
            panels=queries_inner,
        ),
    ]

    ## State stores:
    stores_base = queries_base + 4
    stores_inner = [
        G.TimeSeries(
            title="Put Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_rate{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=stores_base + 0
            ),
        ),
        G.TimeSeries(
            title="Put Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=stores_base + 0
            ),
        ),
        G.TimeSeries(
            title="Put Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=stores_base + 0
            ),
        ),
        G.TimeSeries(
            title="Put if absent Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_rate{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=stores_base + 1
            ),
        ),
        G.TimeSeries(
            title="Put if absent Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=stores_base + 1
            ),
        ),
        G.TimeSeries(
            title="Put if absent Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=stores_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_rate{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=stores_base + 2
            ),
        ),
        G.TimeSeries(
            title="Fetch Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=stores_base + 2
            ),
        ),
        G.TimeSeries(
            title="Fetch Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=stores_base + 2
            ),
        ),
        G.TimeSeries(
            title="Delete Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_rate{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=stores_base + 3
            ),
        ),
        G.TimeSeries(
            title="Delete Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=stores_base + 3
            ),
        ),
        G.TimeSeries(
            title="Delete Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=stores_base + 3
            ),
        ),
        G.TimeSeries(
            title="Restore Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_rate{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=stores_base + 4
            ),
        ),
        G.TimeSeries(
            title="Restore Latency (Avg.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_latency_avg{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=stores_base + 4
            ),
        ),
        G.TimeSeries(
            title="Restore Latency (Max.)",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_latency_max{"
                    + by_thread
                    + "}",
                    legendFormat="{{thread_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=stores_base + 4
            ),
        ),
    ]
    stores_panels = [
        G.RowPanel(
            title="State Stores",
            gridPos=G.GridPos(h=1, w=24, x=0, y=stores_base),
            collapsed=True,
            panels=stores_inner,
        ),
    ]

    # group all panels
    panels = overview_panels + system_panels + queries_panels + stores_panels

    # build dashboard
    return G.Dashboard(
        title="ksqlDB cluster - v2",
        description="Overview of ksqlDB clusters.",
        tags=[
            "confluent",
            "ksqldb",
        ],
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
ksqldb_cluster_label = os.environ.get("KSQLDB_CLUSTER_LABEL", "ksqldb_cluster_id")

# dashboard required by grafanalib
dashboard = dashboard(ds, env_label, server_label, ksqldb_cluster_label)
