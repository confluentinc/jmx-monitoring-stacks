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
            label="Connect cluster",
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
            query='label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns",app="$connect_app"}, connector)',
            multi=True,
            includeAll=True,
        ),
    ]
)

hc_base = 0
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
                expr='count(kafka_connect_app_info{namespace="$ns",app="$connect_app",version!=""})',
                legendFormat="{{version}}",
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
                expr='kafka_connect_connect_worker_rebalance_metrics_time_since_last_rebalance_ms{namespace="$ns",app="$connect_app"} >= 0',
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
    G.Table(
        title="Connect Workers",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_app_info{namespace="$ns",app="$connect_app",start_time_ms!=""}',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='kafka_connect_app_info{namespace="$ns",app="$connect_app",version!=""}',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_connector_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_connector_startup_success_total{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_connector_startup_failure_total{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_task_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_task_startup_success_total{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (pod) (kafka_connect_connect_worker_metrics_task_startup_failure_total{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
        ],
        transformations=[
            {"id": "seriesToColumns", "options": {"byField": "pod"}},
            {
                "id": "filterFieldsByName",
                "options": {
                    "include": {
                        "names": [
                            "pod",
                            "app 1",
                            "start_time_ms",
                            "version",
                            "Value #C",
                            "Value #D",
                            "Value #E",
                            "Value #F",
                            "Value #G",
                            "Value #H",
                            "namespace 1",
                        ]
                    }
                },
            },
            {
                "id": "organize",
                "options": {
                    "excludeByName": {},
                    "indexByName": {
                        "app 1": 1,
                        "namespace 1": 0,
                        "pod": 2,
                        "start_time_ms": 3,
                        "version": 4,
                    },
                    "renameByName": {
                        "Value #C": "connectors",
                        "Value #D": "conn. success",
                        "Value #E": "conn. failure",
                        "Value #F": "tasks",
                        "Value #G": "tasks success",
                        "Value #H": "tasks failure",
                        "app 1": "cluster",
                        "namespace 1": "namespace",
                        "pod": "worker",
                        "start_time_ms": "start time",
                        "version": "version",
                    },
                },
            },
            {
                "id": "convertFieldType",
                "options": {
                    "conversions": [
                        {"destinationType": "number", "targetField": "start_time_ms"}
                    ],
                    "fields": {},
                },
            },
        ],
        gridPos=G.GridPos(h=defaultHeight, w=24, x=0, y=hc_base + 1),
    ),
    G.Table(
        title="Connectors",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_info{namespace="$ns",app="$connect_app"}',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (connector) (kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (connector) (kafka_connect_connect_worker_metrics_connector_running_task_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (connector) (kafka_connect_connect_worker_metrics_connector_failed_task_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
            G.Target(
                expr='sum by (connector) (kafka_connect_connect_worker_metrics_connector_paused_task_count{namespace="$ns",app="$connect_app"})',
                format="table",
                instant=True,
            ),
        ],
        transformations=[
            {"id": "seriesToColumns", "options": {"byField": "connector"}},
            {
                "id": "filterFieldsByName",
                "options": {
                    "include": {
                        "names": [
                            "connector",
                            "Value #B",
                            "Value #C",
                            "Value #D",
                            "Value #E",
                        ]
                    }
                },
            },
            {
                "id": "organize",
                "options": {
                    "excludeByName": {},
                    "renameByName": {
                        "Value #B": "tasks",
                        "Value #C": "running",
                        "Value #D": "failed",
                        "Value #E": "paused",
                    },
                },
            },
        ],
        gridPos=G.GridPos(h=defaultHeight, w=24, x=0, y=hc_base + 2),
    ),

    G.TimeSeries(
        title="Tasks Running Ratio",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_task_metrics_running_ratio{namespace="$ns",app="$connect_app"}',
                legendFormat="{{connector}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=12, x=0, y=hc_base + 3),
    ),
    G.TimeSeries(
        title="Rebalance Latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_worker_rebalance_metrics_rebalance_avg_time_ms{namespace="$ns",app="$connect_app"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=defaultHeight * 2, w=12, x=12, y=hc_base + 3),
    ),
]

system_base = hc_base + 4
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

worker_base = system_base + 1
worker_inner = [
    G.TimeSeries(
        title="Incoming Byte Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_incoming_byte_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="binBps",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=worker_base),
    ),
    G.TimeSeries(
        title="Outgoing Byte Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_outgoing_byte_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="binBps",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=worker_base),
    ),
    G.TimeSeries(
        title="IO Ratio",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_io_ratio{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=worker_base + 1
        ),
    ),
    G.TimeSeries(
        title="Network IO Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_network_io_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="binBps",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=worker_base + 1
        ),
    ),
    G.TimeSeries(
        title="Active Connections",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_connection_count{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=worker_base + 2
        ),
    ),
    G.TimeSeries(
        title="Authentications",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connect_metrics_successful_authentication_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}} (success)",
            ),
            G.Target(
                expr='kafka_connect_connect_metrics_failed_authentication_total{namespace="$ns",app="$connect_app",pod=~"$connect_worker"}',
                legendFormat="{{pod}} (failed)",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=worker_base + 2
        ),
    ),
]
worker_panels = [
    G.RowPanel(
        title="Connect Workers",
        gridPos=G.GridPos(h=1, w=24, x=0, y=worker_base),
        collapsed=True,
        panels=worker_inner,
    ),
]

tasks_base = worker_base + 1
tasks_inner = [
    G.TimeSeries(
        title="Batch Size (Avg.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_task_metrics_batch_size_avg{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=tasks_base
        ),
    ),
    G.TimeSeries(
        title="Batch Size (Max.)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_task_metrics_batch_size_max{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=tasks_base
        ),
    ),
    
    G.TimeSeries(
        title="Offset commit success %",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_task_metrics_offset_commit_success_percentage{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=tasks_base + 1
        ),
    ),
    G.TimeSeries(
        title="Offset commit avg. latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_connector_task_metrics_offset_commit_avg_time_ms{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=tasks_base + 1
        ),
    ),
]
tasks_panels = [
    G.RowPanel(
        title="Tasks",
        gridPos=G.GridPos(h=1, w=24, x=0, y=tasks_base),
        collapsed=True,
        panels=tasks_inner,
    ),
]

task_errors_base = tasks_base + 2
task_errors_inner = [
    G.TimeSeries(
        title="Total Record Failures",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_total_record_failures{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=task_errors_base
        ),
    ),
    G.TimeSeries(
        title="Total Record Error",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_total_record_errors{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=task_errors_base
        ),
    ),
    G.TimeSeries(
        title="Total Records Skipped",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_total_records_skipped{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=task_errors_base
        ),
    ),
    G.TimeSeries(
        title="Total Errors Logged",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_total_errors_logged{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=task_errors_base + 1
        ),
    ),
    G.TimeSeries(
        title="Total Retries",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_total_retries{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=task_errors_base + 1
        ),
    ),
    G.TimeSeries(
        title="Dead Letter Topic Requests",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_task_error_metrics_deadletterqueue_produce_requests{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=task_errors_base + 1
        ),
    ),
]
task_errors_panels = [
    G.RowPanel(
        title="Task Errors",
        gridPos=G.GridPos(h=1, w=24, x=0, y=task_errors_base),
        collapsed=True,
        panels=task_errors_inner,
    ),
]

source_base = task_errors_base + 2
source_inner = [
    G.TimeSeries(
        title="Poll Batch Avg. Latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_source_task_metrics_poll_batch_avg_time_ms{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=source_base
        ),
    ),
    G.TimeSeries(
        title="Poll Batch Max. Latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_source_task_metrics_poll_batch_max_time_ms{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=source_base
        ),
    ),
    G.TimeSeries(
        title="Source Record Poll Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_source_task_metrics_source_record_poll_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=source_base + 1
        ),
    ),
    G.TimeSeries(
        title="Source Record Write Rate",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_source_task_metrics_source_record_write_rate{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ops",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=source_base + 1
        ),
    ),
]
source_panels = [
    G.RowPanel(
        title="Source Tasks",
        gridPos=G.GridPos(h=1, w=24, x=0, y=source_base),
        collapsed=True,
        panels=source_inner,
    ),
]

sink_base = source_base + 2
sink_inner = [
    G.TimeSeries(
        title="Put Batch Avg. Latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_sink_task_metrics_put_batch_avg_time_ms{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=sink_base
        ),
    ),
    G.TimeSeries(
        title="Put Batch Max. Latency",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_sink_task_metrics_put_batch_max_time_ms{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=sink_base
        ),
    ),
    G.TimeSeries(
        title="Partition Count",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_connect_sink_task_metrics_partition_count{namespace="$ns",app="$connect_app",pod=~"$connect_worker",connector=~"$connector"}',
                legendFormat="{{connector}}[{{task}}]",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        gridPos=G.GridPos(
            h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=sink_base + 1
        ),
    ),
]
sink_panels = [
    G.RowPanel(
        title="Sink Tasks",
        gridPos=G.GridPos(h=1, w=24, x=0, y=sink_base),
        collapsed=True,
        panels=sink_inner,
    ),
]

panels = hc_panels + system_panels + tasks_panels + task_errors_panels + source_panels + sink_panels + worker_panels

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
