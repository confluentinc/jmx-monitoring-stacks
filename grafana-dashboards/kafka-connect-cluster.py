import os
import grafanalib.core as G


def dashboard(
    env_label="namespace",
    server_label="' + server_label + '",
    connect_cluster_label="app",
):
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
                name="connect_cluster",
                label="Connect cluster",
                dataSource="Prometheus",
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + env_label
                + '="$env"}, '
                + connect_cluster_label
                + ")",
            ),
            G.Template(
                name="connect_worker",
                label="Connect worker",
                dataSource="Prometheus",
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + env_label
                + '="$env",'
                + connect_cluster_label
                + '="$connect_cluster"}, '
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="connector",
                label="Connector",
                dataSource="Prometheus",
                query="label_values(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                + env_label
                + '="$env",'
                + connect_cluster_label
                + '="$connect_cluster"}, connector)',
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
            title="Connect: Online Workers",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="count(kafka_connect_app_info{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",version!=""})',
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
            title="Connect: Sum of Total Tasks",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
            title="Connect: Sum of Running Tasks",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_running_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
            title="Connect: Sum of Paused Tasks",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_paused_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
            title="Connect: Sum of Failed Tasks",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_failed_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
        G.Stat(
            title="Connect: Time since last rebalance",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_worker_rebalance_metrics_time_since_last_rebalance_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"} >= 0',
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
                h=default_height, w=stat_width, x=stat_width * 5, y=hc_base
            ),
        ),
        G.Table(
            title="Connect Workers",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_app_info{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",start_time_ms!=""}',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="kafka_connect_app_info{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",version!=""}',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_startup_success_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_connector_startup_failure_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_startup_success_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by ("
                    + server_label
                    + ") (kafka_connect_connect_worker_metrics_task_startup_failure_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
            gridPos=G.GridPos(h=default_height, w=24, x=0, y=hc_base + 1),
        ),
        G.Table(
            title="Connectors",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_info{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"}',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_total_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_running_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_failed_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
                    format="table",
                    instant=True,
                ),
                G.Target(
                    expr="sum by (connector) (kafka_connect_connect_worker_metrics_connector_paused_task_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"})',
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
            gridPos=G.GridPos(h=default_height, w=24, x=0, y=hc_base + 2),
        ),
        G.TimeSeries(
            title="Tasks Running Ratio",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_running_ratio{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"}',
                    legendFormat="{{connector}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=12, x=0, y=hc_base + 3),
        ),
        G.TimeSeries(
            title="Rebalance Latency",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_worker_rebalance_metrics_rebalance_avg_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster"}',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=12, x=12, y=hc_base + 3),
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
                    expr="irate(process_cpu_seconds_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}[5m])',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(area)(jvm_memory_bytes_used{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(gc)(irate(jvm_gc_collection_seconds_sum{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}[5m]))',
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

    worker_base = system_base + 1
    worker_inner = [
        G.TimeSeries(
            title="Incoming Byte Rate",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_incoming_byte_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_outgoing_byte_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_io_ratio{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_network_io_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_connection_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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
            title="Authentications",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connect_metrics_successful_authentication_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
                    legendFormat="{{" + server_label + "}} (success)",
                ),
                G.Target(
                    expr="kafka_connect_connect_metrics_failed_authentication_total{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker"}',
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

    tasks_base = worker_base + 1
    tasks_inner = [
        G.TimeSeries(
            title="Batch Size (Avg.)",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_batch_size_avg{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
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
            title="Batch Size (Max.)",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_batch_size_max{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=tasks_base
            ),
        ),
        G.TimeSeries(
            title="Offset commit success %",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_success_percentage{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=tasks_base + 1
            ),
        ),
        G.TimeSeries(
            title="Offset commit avg. latency",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_connector_task_metrics_offset_commit_avg_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=tasks_base + 1
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
                    expr="kafka_connect_task_error_metrics_total_record_failures{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_record_errors{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_records_skipped{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=task_errors_base
            ),
        ),
        G.TimeSeries(
            title="Total Errors Logged",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_errors_logged{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_total_retries{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_task_error_metrics_deadletterqueue_produce_requests{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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

    source_base = task_errors_base + 2
    source_inner = [
        G.TimeSeries(
            title="Poll Batch Avg. Latency",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_poll_batch_avg_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
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
            title="Poll Batch Max. Latency",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_poll_batch_max_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=source_base
            ),
        ),
        G.TimeSeries(
            title="Source Record Poll Rate",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_source_record_poll_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=source_base + 1
            ),
        ),
        G.TimeSeries(
            title="Source Record Write Rate",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_source_task_metrics_source_record_write_rate{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ops",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=source_base + 1
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
                    expr="kafka_connect_sink_task_metrics_put_batch_avg_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
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
            title="Put Batch Max. Latency",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_put_batch_max_time_ms{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
                    legendFormat="{{connector}}[{{task}}]",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=sink_base
            ),
        ),
        G.TimeSeries(
            title="Partition Count",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_connect_sink_task_metrics_partition_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '="$connect_cluster",'
                    + server_label
                    + '=~"$connect_worker",connector=~"$connector"}',
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

    panels = (
        hc_panels
        + system_panels
        + tasks_panels
        + task_errors_panels
        + source_panels
        + sink_panels
        + worker_panels
    )

    return G.Dashboard(
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


env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
connect_cluster_label = os.environ.get(
    "CONNECT_CLUSTER_LABEL", "kafka_connect_cluster_id"
)
dashboard = dashboard(env_label, server_label, connect_cluster_label)
