
import grafanalib.core as G

defaultHeight = 5
statWidth = 4
tsWidth = 8

templating = G.Templating(
    list=[
        G.Template(
            name="ns",
            label="Namespace",
            dataSource="Prometheus",
            query="label_values(namespace)",
        ),
        G.Template(
            name="ksqldb_app",
            label="ksqlDB cluster",
            dataSource="Prometheus",
            query='label_values(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns"},app)',
        ),
        G.Template(
            name="ksqldb_cluster_id",
            label="ksqlDB cluster ID",
            dataSource="Prometheus",
            query='label_values(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns"},ksql_cluster)',
            hide=True,
        ),
        G.Template(
            name="ksqldb_server",
            label="ksqlDB server",
            dataSource="Prometheus",
            query='label_values(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns",app="$ksqldb_app"}, pod)',
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
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='count(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns", app="$ksqldb_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=hc_base),
    ),
    G.Stat(
        title="ksqlDB: Sum of Active Queries",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns", app="$ksqldb_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=hc_base),
    ),
    G.Stat(
        title="ksqlDB: Sum of Running Queries",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(ksql_ksql_engine_query_stats_running_queries{namespace="$ns", app="$ksqldb_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="green"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=hc_base),
    ),
    G.Stat(
        title="ksqlDB: Sum of Rebalancing Queries",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(ksql_ksql_engine_query_stats_rebalancing_queries{namespace="$ns", app="$ksqldb_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="yellow"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=hc_base),
    ),
    G.Stat(
        title="Connect: Sum of Failed Queries",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='avg(ksql_ksql_engine_query_stats_error_queries{namespace="$ns", app="$ksqldb_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 4, y=hc_base),
    ),

    G.TimeSeries(
        title="Cluster Liveness",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='ksql_ksql_engine_query_stats_liveness_indicator{namespace="$ns",app="$ksqldb_app"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=0, y=hc_base + 1),
    ),
    G.TimeSeries(
        title="Messages consumed/sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='ksql_ksql_engine_query_stats_messages_consumed_per_sec{namespace="$ns",app="$ksqldb_app"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="cps",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=hc_base + 1),
    ),
    G.TimeSeries(
        title="Messages produced/sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='ksql_ksql_engine_query_stats_messages_produced_per_sec{namespace="$ns",app="$ksqldb_app"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="cps",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=hc_base + 1),
    ),
]

system_base = hc_base + 2
system_panels = [
    G.RowPanel(
        title="System",
        gridPos=G.GridPos(h=1, w=24, x=0, y=system_base),
    ),
    G.TimeSeries(
        title="CPU usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='irate(process_cpu_seconds_total{namespace="$ns",app="$ksqldb_app",type="ksqldb"}[5m])',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=system_base),
    ),
    G.TimeSeries(
        title="Memory usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(area)(jvm_memory_bytes_used{namespace="$ns",app="$ksqldb_app",type="ksqldb"})',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=system_base),
    ),
    G.TimeSeries(
        title="GC collection",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(gc)(irate(jvm_gc_collection_seconds_sum{namespace="$ns",app="$ksqldb_app",type="ksqldb"}[5m]))',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=system_base),
    ),
]

queries_base = system_base + 1
queries_inner = [
    G.TimeSeries(
        title="Poll Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_poll_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=queries_base),
    ),
    G.TimeSeries(
        title="Poll Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_poll_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=queries_base),
    ),

    G.TimeSeries(
        title="Process Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_process_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=queries_base + 1),
    ),
    G.TimeSeries(
        title="Process Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_process_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=queries_base + 1),
    ),

    G.TimeSeries(
        title="Commit Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_commit_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=queries_base + 2),
    ),
    G.TimeSeries(
        title="Commit Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_commit_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=queries_base + 2),
    ),

    G.TimeSeries(
        title="Punctuate Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_punctuate_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=queries_base + 3),
    ),
    G.TimeSeries(
        title="Punctuate Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_thread_metrics_punctuate_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=queries_base + 3),
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
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_rate{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=stores_base + 0),
    ),
    G.TimeSeries(
        title="Put Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=stores_base + 0),
    ),
    G.TimeSeries(
        title="Put Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=stores_base + 0),
    ),

    G.TimeSeries(
        title="Put if absent Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_if_absent_rate{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=stores_base + 1),
    ),
    G.TimeSeries(
        title="Put if absent Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_if_absent_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=stores_base + 1),
    ),
    G.TimeSeries(
        title="Put if absent Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_put_if_absent_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=stores_base + 1),
    ),

    G.TimeSeries(
        title="Fetch Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_fetch_rate{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=stores_base + 2),
    ),
    G.TimeSeries(
        title="Fetch Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_fetch_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=stores_base + 2),
    ),
    G.TimeSeries(
        title="Fetch Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_fetch_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=stores_base + 2),
    ),

    G.TimeSeries(
        title="Delete Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_delete_rate{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=stores_base + 3),
    ),
    G.TimeSeries(
        title="Delete Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_delete_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=stores_base + 3),
    ),
    G.TimeSeries(
        title="Delete Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_delete_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=stores_base + 3),
    ),

    G.TimeSeries(
        title="Restore Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_restore_rate{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=stores_base + 4),
    ),
    G.TimeSeries(
        title="Restore Latency (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_restore_latency_avg{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=stores_base + 4),
    ),
    G.TimeSeries(
        title="Restore Latency (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_streams_stream_state_metrics_restore_latency_max{namespace="$ns",app="$ksqldb_app",pod=~"$ksqldb_server",thread_id=~".+$ksqldb_cluster_id.+"}',
                legendFormat="{{thread_id}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=stores_base + 4),
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

dashboard = G.Dashboard(
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
