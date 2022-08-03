import os
import grafanalib.core as G


def dashboard(
    ds="Prometheus",
    env_label="namespace",
    server_label="' + server_label + '",
    connect_cluster_label="app",
):
    """
    Kafka Connect cluster dashboard
    It includes:
    - Cluster overview
    - System resources
    - Connect workers
    - Tasks
    - Task Errors
    - Source Tasks
    - Sink Tasks

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
    by_cluster = by_env + "," + connect_cluster_label + '="$connect_cluster"'
    by_server = by_cluster + "," + server_label + '=~"$connect_worker"'
    by_connector = by_server + ',connector=~"$connector"'

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
                name="connect_cluster",
                label="Connect cluster",
                dataSource=ds,
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + by_env
                + "}, "
                + connect_cluster_label
                + ")",
            ),
            G.Template(
                name="connect_worker",
                label="Connect worker",
                dataSource=ds,
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + by_cluster
                + "}, "
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="connector",
                label="Connector",
                dataSource=ds,
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + by_cluster
                + "}, connector)",
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
            title="Cluster Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=overview_base),
        ),
        # First level
        G.Stat(
            title="Connect: Online Workers",
            description="""Kafka Connect online workers returning metrics.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(kafka_connect_app_info{"
                    + by_cluster
                    + ',version!=""})',
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
            title="Connect: Sum of Total Tasks",
            description="""Number of tasks deployed on Kafka Connect cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_total_task_count{"
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
            title="Connect: Sum of Running Tasks",
            description="""Number of Running Tasks on the Kafka Connect cluster.
            Ideally, this number should be equal to the total number of tasks deployed.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_running_task_count{"
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
            title="Connect: Sum of Paused Tasks",
            description="""Number of Paused Tasks on the Kafka Connect cluster.
            Ideally, this number should be zero, as tasks should be running.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_paused_task_count{"
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
            title="Connect: Sum of Failed Tasks",
            description="""Number of Paused Tasks on the Kafka Connect cluster.
            Ideally, this number should be zero, as tasks should be running.
            It's recommended alerting when this value is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_failed_task_count{"
                    + by_cluster
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 4, y=overview_base
            ),
        ),
        G.Stat(
            title="Connect: Time since last rebalance",
            description="""Informative value. Time since last rebalance.
            When this value is continuously and repeatedly low means some connectors are failing and rebalancing is triggered constantly.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_worker_rebalance_metrics_time_since_last_rebalance_ms{"
                    + by_cluster
                    + "} >= 0",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            format="clockms",
            graphMode="none",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 5, y=overview_base
            ),
        ),
        # Second level
        G.Table(
            title="Connect Workers",
            description="""Connect workers metadata and stats.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_app_info{" + by_cluster + ',start_time_ms!=""}',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="kafka_connect_app_info{" + by_cluster + ',version!=""}',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_count{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_startup_success_total{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_startup_failure_total{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_count{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_startup_success_total{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_startup_failure_total{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
            ],
            transformations=[
                {"id": "seriesToColumns", "options": {"byField": server_label}},
                {
                    "id": "filterFieldsByName",
                    "options": {
                        "include": {
                            "names": [
                                server_label,
                                connect_cluster_label + " 1",
                                "start_time_ms",
                                "version",
                                "Value #C",
                                "Value #D",
                                "Value #E",
                                "Value #F",
                                "Value #G",
                                "Value #H",
                                env_label + " 1",
                            ]
                        }
                    },
                },
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {},
                        "indexByName": {
                            connect_cluster_label + " 1": 1,
                            env_label + " 1": 0,
                            server_label: 2,
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
                            connect_cluster_label + " 1": "cluster",
                            env_label + " 1": "environment",
                            server_label: "worker",
                            "start_time_ms": "start time",
                            "version": "version",
                        },
                    },
                },
            ],
            gridPos=G.GridPos(h=default_height, w=24, x=0, y=overview_base + 1),
        ),
        # Third level
        G.Table(
            title="Connectors",
            description="""Connectors deployed and task stats.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connector_info{" + by_cluster + "}",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_total_task_count{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_running_task_count{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_failed_task_count{"
                    + by_cluster
                    + "})",
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_paused_task_count{"
                    + by_cluster
                    + "})",
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
            gridPos=G.GridPos(h=default_height, w=24, x=0, y=overview_base + 2),
        ),
        # Forth level
        G.TimeSeries(
            title="Tasks Running Ratio",
            description="""How much time the connector tasks are in running state.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_running_ratio{"
                    + by_cluster
                    + "}",
                    legendFormat="{{connector}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=12, x=0, y=overview_base + 3),
        ),
        G.TimeSeries(
            title="Rebalance Latency (avg.)",
            description="""Average ime spent on rebalance state.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_worker_rebalance_metrics_rebalance_avg_time_ms{"
                    + by_cluster
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=12, x=12, y=overview_base + 3),
        ),
    ]

    ## System resources:
    ### When updating descriptions on these panels, also update descriptions in other cluster dashboards
    system_base = overview_base + 4
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

    ## Workers:
    worker_base = system_base + 1
    worker_inner = [
        G.TimeSeries(
            title="Incoming Byte Rate",
            description="Incoming byte rate per second per worker.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_incoming_byte_rate{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=worker_base
            ),
        ),
        G.TimeSeries(
            title="Outgoing Byte Rate",
            description="Outgoing byte rate per second per worker.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_outgoing_byte_rate{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=worker_base
            ),
        ),
        G.TimeSeries(
            title="IO Ratio",
            description="Fraction of time the I/O thread spent doing I/O",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_io_ratio{" + by_server + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=worker_base + 1
            ),
        ),
        G.TimeSeries(
            title="Network IO Rate",
            description="Average number of network operations (reads or writes) on all connections per second",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_network_io_rate{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=worker_base + 1
            ),
        ),
        G.TimeSeries(
            title="Active Connections",
            description="Number of active connections",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_connection_count{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=worker_base + 2
            ),
        ),
        G.TimeSeries(
            title="Rate of Authentication",
            description="Successful and failed authentications per second.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_successful_authentication_rate{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}} (success)",
                ),
                G.Target(
                    expr="kafka_connect_connect_metrics_failed_authentication_total{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}} (failed)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=worker_base + 2
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

    ## Tasks:
    tasks_base = worker_base + 1
    tasks_inner = [
        G.TimeSeries(
            title="Batch size",
            description="Maximum and average size of the batches processed by the connector task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_batch_size_avg{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (avg.)",
                ),
                G.Target(
                    expr="kafka_connect_connector_task_metrics_batch_size_max{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=tasks_base
            ),
        ),
        G.TimeSeries(
            title="Offset commit success/failure",
            description="Percentage of offset commit successful and failed.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_success_percentage{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (success)",
                ),
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_failure_percentage{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (failure)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=tasks_base
            ),
        ),
        G.TimeSeries(
            title="Offset commit latency",
            description="Average and Maximum time in milliseconds taken by the task to commit offsets",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_avg_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (avg.)",
                ),
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_max_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=tasks_base
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

    ## Task Errors:
    task_errors_base = tasks_base + 1
    task_errors_inner = [
        # First layer
        G.TimeSeries(
            title="Total Record Failures",
            description="Total number of failures seen by task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_record_failures{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=task_errors_base
            ),
        ),
        G.TimeSeries(
            title="Total Record Error",
            description="Total number of errors seen by task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_record_errors{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=task_errors_base
            ),
        ),
        G.TimeSeries(
            title="Total Records Skipped",
            description="Total number of records skipped seen by task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_records_skipped{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=task_errors_base
            ),
        ),
        # Second layer
        G.TimeSeries(
            title="Total Errors Logged",
            description="Total number of records logged seen by task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_errors_logged{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=task_errors_base + 1
            ),
        ),
        G.TimeSeries(
            title="Total Retries",
            description="Total number of retries seen by task.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_retries{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=task_errors_base + 1
            ),
        ),
        G.TimeSeries(
            title="Dead Letter Topic Requests",
            description="Number of produce requests to dead letter topics.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_deadletterqueue_produce_requests{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=task_errors_base + 1
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

    ## Source tasks:
    source_base = task_errors_base + 2
    source_inner = [
        G.TimeSeries(
            title="Poll Batch Latency",
            description="Average and Maximum time in milliseconds taken by this task to poll for a batch of source records",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_poll_batch_avg_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (avg.)",
                ),
                G.Target(
                    expr="kafka_connect_source_task_metrics_poll_batch_max_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=source_base
            ),
        ),
        G.TimeSeries(
            title="Source Record Poll Rate",
            description="""Before transformations are applied, 
            this is the average per-second number of records produced or 
            polled by the task belonging to the named source connector in the worker
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_source_record_poll_rate{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=source_base
            ),
        ),
        G.TimeSeries(
            title="Source Record Write Rate",
            description="""After transformations are applied, 
            this is the average per-second number of records output from the transformations and 
            written to Kafka for the task belonging to the named source connector in the worker 
            (excludes any records filtered out by the transformations)
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_source_record_write_rate{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=source_base
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

    ## Sink tasks:
    sink_base = source_base + 1
    sink_inner = [
        G.TimeSeries(
            title="Put Batch Latency",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_put_batch_avg_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (avg.)",
                ),
                G.Target(
                    expr="kafka_connect_sink_task_metrics_put_batch_max_time_ms{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}] (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=sink_base
            ),
        ),
        G.TimeSeries(
            title="Sink Record Read Rate",
            description="""Before transformations are applied, 
            this is the average per-second number of records read from Kafka 
            for the task belonging to the named sink connector in the worker
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_sink_record_read_rate{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=sink_base
            ),
        ),
        G.TimeSeries(
            title="Sink Record Send Rate",
            description="""After transformations are applied, 
            this is the average per-second number of records output from the transformations and 
            sent to the task belonging to the named sink connector in the worker 
            (excludes any records filtered out by the transformations)
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_sink_record_send_rate{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=sink_base
            ),
        ),
        G.TimeSeries(
            title="Partition Count",
            description="""Number of topic partitions assigned to the task and 
            which belong to the named sink connector in the worker
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_partition_count{"
                    + by_connector
                    + "}",
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=sink_base + 1
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

    # group all panels
    panels = (
        overview_panels
        + system_panels
        + tasks_panels
        + task_errors_panels
        + source_panels
        + sink_panels
        + worker_panels
    )

    # build dashboard
    return G.Dashboard(
        title="Kafka Connect cluster",
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


# main labels to customize dashboard
ds = os.environ.get("DATASOURCE", "Prometheus")
env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
connect_cluster_label = os.environ.get(
    "CONNECT_CLUSTER_LABEL", "kafka_connect_cluster_id"
)

# dashboard required by grafanalib
dashboard = dashboard(ds, env_label, server_label, connect_cluster_label)
