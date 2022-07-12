import os
import grafanalib.core as G


def dashboard(
    ds="Prometheus",
    env_label="namespace",
    server_label="pod",
    connect_cluster_label="app",
    ksqldb_cluster_label="app",
):
    """
    Confluent Platform dashboard
    It includes all Confluent components:
    - Zookeeper
    - Kafka
    - Schema Registry
    - Kafka Connect (repeated per cluster)
    - ksqlDB (repeated per cluster)

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

    # Queries
    by_env = env_label + '="$env"'

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
                label="Kafka Connect cluster",
                dataSource=ds,
                query="label_values(kafka_connect_connect_worker_metrics_connector_count{"
                + by_env
                + "}, "
                + connect_cluster_label
                + ")",
                hide=True,
            ),
            G.Template(
                name="ksqldb_cluster",
                label="ksqlDB cluster",
                dataSource=ds,
                query="label_values(ksql_ksql_engine_query_stats_liveness_indicator{"
                + by_env
                + "}, "
                + ksqldb_cluster_label
                + ")",
                hide=True,
            ),
        ]
    )

    # Panel groups
    ## Zookeeper panes:
    ### When updating descriptions on these panels, also update descriptions in zookeeper-cluster.py
    zk_panels = [
        G.RowPanel(
            title="Zookeeper cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="ZK: Quorum Size",
            description="""Quorum Size of Zookeeper ensemble.
            Count Zookeeper servers with quorum size metric.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(zookeeper_status_quorumsize{" + by_env + "})",
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
            dataSource=ds,
            targets=[
                G.Target(
                    expr="avg(zookeeper_inmemorydatatree_nodecount{" + by_env + "})",
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
            dataSource=ds,
            targets=[
                G.Target(
                    expr="zookeeper_numaliveconnections{"
                    + by_env
                    + "} / zookeeper_maxclientcnxnsperhost{"
                    + by_env
                    + "}",
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
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(zookeeper_inmemorydatatree_watchcount{" + by_env + "})",
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
            dataSource=ds,
            targets=[
                G.Target(
                    expr="zookeeper_outstandingrequests{" + by_env + "}",
                    legendFormat="{{pod}} ({{server_id}}:{{member_type}})",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "last"],
            legendPlacement="right",
            gridPos=G.GridPos(h=default_height, w=8, x=stat_width * 4, y=0),
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="yellow"),
                G.Threshold(index=2, value=10.0, color="red"),
            ],
        ),
    ]

    ## Kafka panels
    ### When updating descriptions on these panels, also update descriptions in kafka-cluster.py
    kafka_panels = [
        G.RowPanel(
            title="Kafka cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=1),
        ),
        G.Stat(
            title="Kafka: Online Brokers",
            description="""Count of brokers available (online).
            This value is referential and should not be used for alerting.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(kafka_server_replicamanager_leadercount{"
                    + by_env
                    + "})",
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
            description="""Active Controller broker.
            It should always be 1. If the value is different than 1, then it must be alerted for troubleshooting.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_controller_kafkacontroller_activecontrollercount{"
                    + by_env
                    + "} > 0",
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
            title="Kafka: Sum of Partitions",
            description="""Sum of Topic partitions across the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_partitioncount{"
                    + by_env
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Under-Replicated Partitions (URP)",
            description="""Sum of Under-Replicated Partitions. This is caused by broker or volumes unavailable, impacting replicas to be offline, and reducing the ISR set for those partitions.
            There are transient scenarios that could lead to this number growing (e.g. broker restart), but if the number doesn't shrink in a short period of time (e.g. 1 minute), then it's recommended to alert.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_underreplicatedpartitions{"
                    + by_env
                    + "})",
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
            title="Kafka: Sum of Under-MinISR Partitions",
            description="""Number of partitions where the number of replicas offline is higher than the minimum ISR configuration.
            This means partitions are not available for Producers with acks=all.
            It's recommended alerting when this values is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_cluster_partition_underminisr{" + by_env + "})",
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
            title="Kafka: Sum of Offline Partitions",
            description="""Number of partitions where all replicas are offline.
            Producers and Consumers are affected by this condition.
            It's recommended alerting when this values is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_offlinepartitionscount{"
                    + by_env
                    + "})",
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

    ## Schema Registry panels:
    ### When updating descriptions on these panels, also update descriptions in schema-registry-cluster.py
    sr_panels = [
        G.RowPanel(
            title="Schema Registry cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=2),
        ),
        G.Stat(
            title="SR: Online instances",
            description="""Schema Registry online instances returning metrics.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(kafka_schema_registry_registered_count{"
                    + by_env
                    + "})",
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
            title="SR: Registered Schemas (avg.)",
            description="""Average number of registered schemas across the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="avg(kafka_schema_registry_registered_count{" + by_env + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=2),
        ),
        G.Stat(
            title="SR: Schemas Created by Type (avg.)",
            description="""Average number of schemas created, by type.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="avg(kafka_schema_registry_schemas_created{"
                    + by_env
                    + "}) by (schema_type)",
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
            title="SR: Schemas Deleted by Type (avg.)",
            description="""Average number of schemas deleted, by type.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_schema_registry_schemas_deleted{"
                    + by_env
                    + "}) by (schema_type)",
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

    ## Kafka Connect cluster panels:
    ### When updating descriptions on these panels, also update descriptions in kafka-connect-cluster.py
    connect_inner = [
        G.Stat(
            title="Connect: Online Workers",
            description="""Kafka Connect online workers returning metrics.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(kafka_connect_connect_worker_metrics_connector_count{"
                    + by_env
                    + ","
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
            description="""Number of tasks deployed on Kafka Connect cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_total_task_count{"
                    + by_env
                    + ","
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
            description="""Number of Running Tasks on the Kafka Connect cluster.
            Ideally, this number should be equal to the total number of tasks deployed.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_running_task_count{"
                    + by_env
                    + ","
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
            description="""Number of Paused Tasks on the Kafka Connect cluster.
            Ideally, this number should be zero, as tasks should be running.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_paused_task_count{"
                    + by_env
                    + ","
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
            description="""Number of Paused Tasks on the Kafka Connect cluster.
            Ideally, this number should be zero, as tasks should be running.
            It's recommended alerting when this value is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_connect_connect_worker_metrics_connector_failed_task_count{"
                    + by_env
                    + ","
                    + connect_cluster_label
                    + '=~"$connect_cluster"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=3),
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
                    + by_env
                    + ","
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
    ### Repeat as there could be multiple connect clusters per environment.
    connect_panels = [
        G.RowPanel(
            title="Kafka Connect cluster: $connect_cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=3),
            repeat=G.Repeat(variable="connect_cluster"),
            collapsed=True,
            panels=connect_inner,
        ),
    ]

    ## ksqlDB cluster panels:
    ### When updating descriptions on these panels, also update descriptions in ksqldb-cluster.py
    ksqldb_inner = [
        G.Stat(
            title="ksqlDB: Online instances",
            description="""ksqlDB online instances returning metrics.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="count(ksql_ksql_engine_query_stats_num_active_queries{"
                    + by_env
                    + ","
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
            description="""Number of active queries deployed in the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_num_active_queries{"
                    + by_env
                    + ","
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
            description="""Number of running queries deployed in the cluster.
            Ideally, this number should be equal to the number of active queries as queries should be running.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_running_queries{"
                    + by_env
                    + ","
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
            description="""Number of queries rebalancing in the cluster.
            Ideally, this number should be equal zero, or return to zero in a short period (e.g. 1 minute).
            It's recommended to alert if the number of rebalancing queries stay higher than 0 for a longer period of time.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(ksql_ksql_engine_query_stats_rebalancing_queries{"
                    + by_env
                    + ","
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
            title="Connect: Sum of Queries Failed",
            description="""Number of queries failed in the cluster.
            Ideally, this number should be equal zero.
            It's recommended to alert if the number of queries failed is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="avg(ksql_ksql_engine_query_stats_error_queries{"
                    + by_env
                    + ","
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
    ### Repeat as there could be multiple ksqldb clusters per environment.
    ksqldb_panels = [
        G.RowPanel(
            title="ksqlDB cluster: $ksqldb_cluster",
            gridPos=G.GridPos(h=1, w=24, x=0, y=4),
            repeat=G.Repeat(variable="ksqldb_cluster"),
            collapsed=True,
            panels=ksqldb_inner,
        ),
    ]

    # group all panels
    panels = zk_panels + kafka_panels + sr_panels + connect_panels + ksqldb_panels

    # build dashboard
    return G.Dashboard(
        title="Confluent Platform overview",
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


# main labels to customize dashboard
ds = os.environ.get("DATASOURCE", "Prometheus")
env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
connect_cluster_label = os.environ.get(
    "CONNECT_CLUSTER_LABEL", "kafka_connect_cluster_id"
)
ksqldb_cluster_label = os.environ.get("KSQLDB_CLUSTER_LABEL", "ksqldb_cluster_id")

# dashboard required by grafanalib
dashboard = dashboard(
    ds, env_label, server_label, connect_cluster_label, ksqldb_cluster_label
)
