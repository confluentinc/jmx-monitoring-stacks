import os
import grafanalib.core as G


def dashboard(env_label="namespace", server_label="pod", ksqldb_cluster_label="app"):
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
                name="ksqldb_cluster",
                label="ksqlDB cluster",
                dataSource="Prometheus",
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + env_label
                + '="$env"},'
                + ksqldb_cluster_label
                + ")",
            ),
            G.Template(
                name="ksqldb_cluster_id",
                label="ksqlDB cluster ID",
                dataSource="Prometheus",
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + env_label
                + '="$env"},ksql_cluster)',
                hide=2,  # true
            ),
            G.Template(
                name="ksqldb_server",
                label="ksqlDB server",
                dataSource="Prometheus",
                query="label_values(ksql_ksql_engine_query_stats_num_active_queries{"
                + env_label
                + '="$env",'
                + ksqldb_cluster_label
                + '="$ksqldb_cluster"}, '
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    hc_base = 0
    hc_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=hc_base),
        ),
        G.Stat(
            title="ksqlDB: Online Servers",
            description="""ksqlDB online instances returning metrics.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="count(ksql_ksql_engine_query_stats_num_active_queries{"
                    + env_label
                    + '="$env", '
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 0, y=hc_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Active Queries",
            description="""Number of active queries deployed in the cluster.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_num_active_queries{"
                    + env_label
                    + '="$env", '
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 1, y=hc_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Running Queries",
            description="""Number of running queries deployed in the cluster.
            Ideally, this number should be equal to the number of active queries as queries should be running.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_running_queries{"
                    + env_label
                    + '="$env", '
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="green"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 2, y=hc_base
            ),
        ),
        G.Stat(
            title="ksqlDB: Sum of Rebalancing Queries",
            description="""Number of queries rebalancing in the cluster.
            Ideally, this number should be equal zero, or return to zero in a short period (e.g. 1 minute).
            It's recommended to alert if the number of rebalancing queries stay higher than 0 for a longer period of time.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_rebalancing_queries{"
                    + env_label
                    + '="$env", '
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="yellow"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 3, y=hc_base
            ),
        ),
        G.Stat(
            title="Connect: Sum of Queries Failed",
            description="""Number of queries failed in the cluster.
            Ideally, this number should be equal zero.
            It's recommended to alert if the number of queries failed is higher than 0.
            """,
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="avg(ksql_ksql_engine_query_stats_error_queries{"
                    + env_label
                    + '="$env", '
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 4, y=hc_base
            ),
        ),
        G.TimeSeries(
            title="Cluster Liveness",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_liveness_indicator{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=0, y=hc_base + 1),
        ),
        G.TimeSeries(
            title="Messages consumed/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_messages_consumed_per_sec{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=hc_base + 1
            ),
        ),
        G.TimeSeries(
            title="Messages produced/sec",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="ksql_ksql_engine_query_stats_messages_produced_per_sec{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=hc_base + 1
            ),
        ),
    ]

    ## System resources:
    ### When updating descriptions on these panels, also update descriptions in other cluster dashboards
    system_base = hc_base + 2
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="irate(process_cpu_seconds_total{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server"}[5m])',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum without(area)(jvm_memory_bytes_used{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server"})',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="sum without(gc)(irate(jvm_gc_collection_seconds_sum{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server"}[5m]))',
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

    queries_base = system_base + 1
    queries_inner = [
        G.TimeSeries(
            title="Poll Latency (Avg.)",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_poll_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_poll_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_process_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_process_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_commit_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_commit_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_punctuate_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_thread_metrics_punctuate_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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

    stores_base = queries_base + 4
    stores_inner = [
        G.TimeSeries(
            title="Put Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_rate{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_rate{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_put_if_absent_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_rate{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_fetch_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_rate{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_delete_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_rate{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_latency_avg{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="kafka_streams_stream_state_metrics_restore_latency_max{"
                    + env_label
                    + '="$env",'
                    + ksqldb_cluster_label
                    + '="$ksqldb_cluster",'
                    + server_label
                    + '=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
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

    panels = hc_panels + system_panels + queries_panels + stores_panels

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


env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
ksqldb_cluster_label = os.environ.get("KSQLDB_CLUSTER_LABEL", "ksqldb_cluster_id")
dashboard = dashboard(env_label, server_label, ksqldb_cluster_label)
