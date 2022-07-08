import os
import grafanalib.core as G


def dashboard(
    env_label="namespace",
    server_label="pod",
    connect_cluster_label="app",
    ksqldb_cluster_label="app",
):
    default_height = 5
    stat_width = 4

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
                label="Kafka Connect cluster",
                dataSource="Prometheus",
                query="label_values(kafka_connect_connect_worker_metrics_connector_count{"
                + env_label
                + '="$env"}, '
                + connect_cluster_label
                + ")",
                hide=True,
            ),
            G.Template(
                name="ksqldb_cluster",
                label="ksqlDB cluster",
                dataSource="Prometheus",
                query="label_values(ksql_ksql_engine_query_stats_liveness_indicator{"
                + env_label
                + '="$env"}, '
                + ksqldb_cluster_label
                + ")",
                hide=True,
            ),
        ]
    )

    zk_panels = [
        G.RowPanel(
            title="Zookeeper cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="ZK: Quorum Size",
            dataSource="${DS_PROMETHEUS}",
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
            title="ZK: Avg. number of ZNodes",
            dataSource="${DS_PROMETHEUS}",
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
            title="ZK: Sum of number of Alive Connections",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(zookeeper_numaliveconnections{" + env_label + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=0),
        ),
        G.Stat(
            title="ZK: Sum of watchers",
            dataSource="${DS_PROMETHEUS}",
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="zookeeper_outstandingrequests{" + env_label + '="$env"}',
                    legendFormat="{{pod}} ({{server_id}}:{{member_type}})",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "last"],
            legendPlacement="right",
            gridPos=G.GridPos(h=default_height, w=8, x=stat_width * 4, y=0),
        ),
    ]

    kafka_panels = [
        G.RowPanel(
            title="Kafka cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=1),
        ),
        G.Stat(
            title="Kafka: Online Brokers",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="count(kafka_server_replicamanager_leadercount{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=1),
        ),
        G.Stat(
            title="Kafka: Active Controller",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_controller_kafkacontroller_activecontrollercount{"
                    + env_label
                    + '="$env"} > 0',
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            textMode="value_and_name",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Partitioenv",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_partitioncount{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Partitions Under-Replicated (URP)",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_underreplicatedpartitions{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Partitioenv Under-MinISR",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_cluster_partition_underminisr{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Partitions Offline",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_offlinepartitionscount{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 5, y=1),
        ),
    ]

    sr_panels = [
        G.RowPanel(
            title="Schema Registry cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=2),
        ),
        G.Stat(
            title="SR: Online instances",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="count(kafka_schema_registry_registered_count{"
                    + env_label
                    + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="red"),
                G.Threshold(index=1, value=1.0, color="yellow"),
                G.Threshold(index=2, value=2.0, color="green"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=2),
        ),
        G.Stat(
            title="SR: Sum of Registered Schemas",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="avg(kafka_schema_registry_registered_count{"
                    + env_label
                    + '="$env"})',
                    instant=True,
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=2),
        ),
        G.Stat(
            title="SR: Sum of Created Schemas by Type",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="avg(kafka_schema_registry_schemas_created{"
                    + env_label
                    + '="$env"}) by (schema_type)',
                    legendFormat="{{schema_type}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=2),
        ),
        G.Stat(
            title="SR: Sum of Deleted Schemas by Type",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_schema_registry_schemas_deleted{"
                    + env_label
                    + '="$env"}) by (schema_type)',
                    legendFormat="{{schema_type}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=2),
        ),
    ]

    connect_inner = [
        G.Stat(
            title="Connect: Online Workers",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="count(kafka_connect_connect_worker_metrics_connector_count{"
                    + env_label
                    + '="$env",'
                    + connect_cluster_label
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=3),
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
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=3),
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
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="green"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=3),
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
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="yellow"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=3),
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
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=3),
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
                    + '=~"$connect_cluster"} >= 0',
                    legendFormat="{{pod}}",
                ),
            ],
            reduceCalc="last",
            format="clockms",
            graphMode="none",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 5, y=3),
        ),
    ]

    connect_panels = [
        G.RowPanel(
            title="Kafka Connect cluster: $connect_cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=3),
            repeat=G.Repeat(variable="connect_cluster"),
            collapsed=True,
            panels=connect_inner,
        ),
    ]

    ksqldb_inner = [
        G.Stat(
            title="ksqlDB: Online Servers",
            dataSource="${DS_PROMETHEUS}",
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=4),
        ),
        G.Stat(
            title="ksqlDB: Sum of Active Queries",
            dataSource="${DS_PROMETHEUS}",
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=4),
        ),
        G.Stat(
            title="ksqlDB: Sum of Running Queries",
            dataSource="${DS_PROMETHEUS}",
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=4),
        ),
        G.Stat(
            title="ksqlDB: Sum of Rebalancing Queries",
            dataSource="${DS_PROMETHEUS}",
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=4),
        ),
        G.Stat(
            title="Connect: Sum of Failed Queries",
            dataSource="${DS_PROMETHEUS}",
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=4),
        ),
    ]

    ksqldb_panels = [
        G.RowPanel(
            title="ksqlDB cluster: $ksqldb_cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=4),
            repeat=G.Repeat(variable="ksqldb_cluster"),
            collapsed=True,
            panels=ksqldb_inner,
        ),
    ]

    panels = zk_panels + kafka_panels + sr_panels + connect_panels + ksqldb_panels

    return G.Dashboard(
        title="Confluent Platform overview - v2",
        description="Overview of the main health-check metrics from Confluent Platform components.",
        tags=[
            "confluent",
            "kafka",
            "zookeeper",
            "kafka-connect",
            "schema-registry",
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
connect_cluster_label = os.environ.get(
    "CONNECT_CLUSTER_LABEL", "kafka_connect_cluster_id"
)
ksqldb_cluster_label = os.environ.get("KSQLDB_CLUSTER_LABEL", "ksqldb_cluster_id")
dashboard = dashboard(
    env_label, server_label, connect_cluster_label, ksqldb_cluster_label
)
