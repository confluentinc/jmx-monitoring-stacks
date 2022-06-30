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
            name="connect_app",
            label="Connect group",
            dataSource="Prometheus",
            query='label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns"}, app)',
        ),
        G.Template(
            name="connect_worker",
            label="Connect worker",
            dataSource="Prometheus",
            query='label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns",app="$connect_app"}, pod)',
            multi=True,
            includeAll=True,
        ),
        G.Template(
            name="connector",
            label="Connector",
            dataSource="Prometheus",
            query='label_values(kafka_connect_connector_task_metrics_pause_ratio{namespace="$ns",app="$connector_app"}, connector)',
        ),
    ]
)

hc_base=0
hc_panels = [
    G.RowPanel(
        title="Health-check",
        gridPos=G.GridPos(h=1, w=24, x=0, y=hc_base),
    ),
    G.Stat(
        title="Connect: Online Workers",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='count(kafka_connect_app_info{namespace="$ns",app="$connect_app"})',
                legendFormat='{{version}}'
            ),
        ],
        reduceCalc="last",
        textMode="value_and_name",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=hc_base),
    ),
    G.Stat(
        title="Connect: Sum of Total Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns",app="$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=hc_base),
    ),
    G.Stat(
        title="Connect: Sum of Running Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_running_task_count{namespace="$ns",app="$connect_app"})',
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
        title="Connect: Sum of Paused Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_paused_task_count{namespace="$ns",app="$connect_app"})',
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
        title="Connect: Sum of Failed Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_failed_task_count{namespace="$ns",app="$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 4, y=hc_base),
    ),
    G.Stat(
        title="Connect: Time since last rebalance",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_worker_rebalance_metrics_time_since_last_rebalance_ms{namespace="$ns",app=~"$connect_app"} >= 0',
                legendFormat="{{pod}}",
            ),
        ],
        reduceCalc="last",
        format="clockms",
        graphMode="none",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 5, y=hc_base),
    ),
]

system_base=hc_base + 1;
system_panels=[
    G.RowPanel(
        title="System",
        gridPos=G.GridPos(h=1, w=24, x=0, y=system_base),
    ),
    G.TimeSeries(
        title="CPU usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='irate(process_cpu_seconds_total{namespace="$ns",app="$connect_app",type="connect"}[5m])',
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
                expr='sum without(area)(jvm_memory_bytes_used{namespace="$ns",app="$connect_app",type="connect"})',
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
                expr='sum without(gc)(irate(jvm_gc_collection_seconds_sum{namespace="$ns",app="$connect_app",type="connect"}[5m]))',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=system_base),
    ),
]

panels = hc_panels + system_panels

dashboard = G.Dashboard(
    title="Kafka Connect cluster - v2",
    description="Overview of the Kafka Connect cluster",
    tags=["confluent", "kafka-connect"],
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
