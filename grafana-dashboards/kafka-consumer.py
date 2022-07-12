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
                name="server",
                label="Server",
                dataSource="Prometheus",
                query="label_values(kafka_consumer_consumer_metrics_incoming_byte_rate{"
                + env_label
                + '="$env", client_type="consumer"},'
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="client_id",
                label="Client ID",
                dataSource="Prometheus",
                query="label_values(kafka_consumer_consumer_metrics_incoming_byte_rate{"
                + env_label
                + '="$env", client_type="consumer"},client_id)',
                multi=True,
                includeAll=True,
            ),
        ]
    )

    topk = "10"

    overview_base = 0
    overview_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="Record Consumed Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate{"
                    + env_label
                    + '="$env", client_type="producer", client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"} > 0)',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=0),
        ),
        G.Stat(
            title="Records Lag",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate{"
                    + env_label
                    + '="$env", client_type="producer", client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"} > 0)',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=0),
        ),
        G.Stat(
            title="Rebalance Rate per hour",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", kafka_consumer_consumer_coordinator_metrics_rebalance_rate_per_hour{"
                    + env_label
                    + '="$env", client_type="producer", client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"} > 0)',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="yellow"),
                G.Threshold(index=2, value=10.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=0),
        ),
        G.Stat(
            title="Failed Rebalance Rate per hour",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ", kafka_consumer_consumer_coordinator_metrics_failed_rebalance_rate_per_hour{"
                    + env_label
                    + '="$env", client_type="producer", client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"} > 0)',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=0),
        ),
        G.Stat(
            title="Versions",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="count(kafka_consumer_app_info{"
                    + env_label
                    + '="$env", client_id=~"$client_id", version!="", '
                    + server_label
                    + '=~"$server"}) by (version)',
                    legendFormat="{{version}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=0),
        ),
    ]

    performance_base = overview_base + 1
    performance_inner = [
        G.TimeSeries(
            title="Bytes Consumed Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_bytes_consumed_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base
            ),
        ),
        G.TimeSeries(
            title="Records Consumed Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cts",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base
            ),
        ),
        G.TimeSeries(
            title="Records Lag Max",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_records_lag_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base
            ),
        ),
        G.TimeSeries(
            title="Fetch Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch Latency",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_latency_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_latency_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch Size",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_size_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_size_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch Throttle Time",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_throttle_time_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_throttle_time_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 2
            ),
        ),
    ]
    performance_panels = [
        G.RowPanel(
            title="Performance",
            gridPos=G.GridPos(h=1, w=24, x=0, y=performance_base),
            collapsed=True,
            panels=performance_inner,
        ),
    ]

    group_base = performance_base + 3
    group_inner = [
        G.TimeSeries(
            title="Commit Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_commit_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 0
            ),
        ),
        G.TimeSeries(
            title="Join Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_join_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base + 0
            ),
        ),
        G.TimeSeries(
            title="Sync Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_sync_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base + 0
            ),
        ),
        G.TimeSeries(
            title="Commit Latency",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_commit_latency_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_commit_latency_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Join Time",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_join_time_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_join_time_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Sync Time",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_sync_time_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_sync_time_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base + 1
            ),
        ),
        G.TimeSeries(
            title="Heartbeat Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_heartbeat_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 2
            ),
        ),
        G.TimeSeries(
            title="Heartbeat Response Time (Max.)",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_heartbeat_response_time_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base + 2
            ),
        ),
        G.TimeSeries(
            title="Last Heartbeat Seconds Ago",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_last_heartbeat_seconds_ago{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="s",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base + 2
            ),
        ),
        G.TimeSeries(
            title="Rebalance Rate Per Hour",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_rebalance_rate_per_hour{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_failed_rebalance_rate_per_hour{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (failed)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=performance_base + 3
            ),
        ),
        G.TimeSeries(
            title="Rebalance Latency",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_rebalance_latency_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_rebalance_latency_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=performance_base + 3
            ),
        ),
        G.TimeSeries(
            title="Assigned Partitions",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_coordinator_metrics_assigned_partitions{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=performance_base + 3
            ),
        ),
    ]
    group_panels = [
        G.RowPanel(
            title="Consumer group",
            gridPos=G.GridPos(h=1, w=24, x=0, y=group_base),
            collapsed=True,
            panels=group_inner,
        ),
    ]

    connection_base = group_base + 4
    connection_inner = [
        G.TimeSeries(
            title="Connection Count",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_connection_count{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=connection_base
            ),
        ),
        G.TimeSeries(
            title="Connection Creation Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_connection_creation_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=connection_base
            ),
        ),
        G.TimeSeries(
            title="Connection Close Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_connection_close_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=connection_base
            ),
        ),
        G.TimeSeries(
            title="IO ratio",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_io_ratio{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            # unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=connection_base + 1
            ),
        ),
        G.TimeSeries(
            title="IO wait ratio",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_io_wait_ratio{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            # unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=connection_base + 1
            ),
        ),
        G.TimeSeries(
            title="Select Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_select_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=connection_base + 1
            ),
        ),
        G.TimeSeries(
            title="IO time avg.",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_io_time_ns_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ns",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=connection_base + 2
            ),
        ),
        G.TimeSeries(
            title="IO wait time avg.",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_metrics_io_wait_time_ns_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ns",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=connection_base + 2
            ),
        ),
    ]
    connection_panels = [
        G.RowPanel(
            title="Connections",
            gridPos=G.GridPos(h=1, w=24, x=0, y=connection_base),
            collapsed=True,
            panels=connection_inner,
        ),
    ]

    per_broker_base = connection_base + 3
    per_broker_inner = [
        G.TimeSeries(
            title="Incoming Byte Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_incoming_byte_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} <- {{node_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=per_broker_base
            ),
        ),
        G.TimeSeries(
            title="Outgoing Byte Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_outgoing_byte_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} -> {{node_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=per_broker_base
            ),
        ),
        G.TimeSeries(
            title="Request Latency",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_request_latency_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} -> {{node_id}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_request_latency_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} -> {{node_id}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=per_broker_base
            ),
        ),
        G.TimeSeries(
            title="Request Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_request_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} -> {{node_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=per_broker_base + 1
            ),
        ),
        G.TimeSeries(
            title="Response Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_node_metrics_response_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} <- {{node_id}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=per_broker_base + 1
            ),
        ),
    ]
    per_broker_panels = [
        G.RowPanel(
            title="Per Broker",
            gridPos=G.GridPos(h=1, w=24, x=0, y=per_broker_base),
            collapsed=True,
            panels=per_broker_inner,
        ),
    ]

    per_topic_base = per_broker_base + 2
    per_topic_inner = [
        G.TimeSeries(
            title="Bytes Consumed Rate per Topic",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_bytes_consumed_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} <- {{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=per_broker_base + 0
            ),
        ),
        G.TimeSeries(
            title="Records Consumed Rate per Topic",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} <- {{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=per_broker_base + 0
            ),
        ),
        G.TimeSeries(
            title="Fetch Size per Topic",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_size_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} <- {{topic}} (avg.)",
                ),
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_fetch_size_max{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{"
                    + server_label
                    + "}} <- {{topic}} (max.)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=per_broker_base + 1
            ),
        ),
        G.TimeSeries(
            title="Records per Request Avg. per Topic",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_consumer_consumer_fetch_manager_metrics_records_per_request_avg{"
                    + env_label
                    + '="$env",client_id=~"$client_id", '
                    + server_label
                    + '=~"$server"})',
                    legendFormat="{{client_id}}@{{" + server_label + "}} <- {{topic}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=per_broker_base + 0
            ),
        ),
    ]
    per_topic_panels = [
        G.RowPanel(
            title="Per Topic",
            gridPos=G.GridPos(h=1, w=24, x=0, y=per_topic_base),
            collapsed=True,
            panels=per_topic_inner,
        ),
    ]

    panels = (
        overview_panels
        + performance_panels
        + group_panels
        + connection_panels
        + per_broker_panels
        + per_topic_panels
    )

    return G.Dashboard(
        title="Kafka Consumer - v2",
        description="Overview of the Kafka consumers",
        tags=["confluent", "kafka-client", "kafka-consumer"],
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
