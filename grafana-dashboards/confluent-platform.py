import grafanalib.core as G

defaultHeight = 5
statWidth = 4

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
            label="Kafka Connect cluster",
            dataSource="Prometheus",
            query='label_values(kafka_connect_connect_worker_metrics_connector_count{namespace="$ns"}, app)',
            hide=2,
        ),
        G.Template(
            name="ksqldb_app",
            label="ksqlDB cluster",
            dataSource="Prometheus",
            query='label_values(ksql_ksql_engine_query_stats_num_active_queries{namespace="$ns"},app)',
            hide=2,
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
                expr='count(zookeeper_status_quorumsize{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="red"),
            G.Threshold(index=1, value=2.0, color="yellow"),
            G.Threshold(index=2, value=3.0, color="green"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=0),
    ),
    G.Stat(
        title="ZK: Avg. number of ZNodes",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='avg(zookeeper_inmemorydatatree_nodecount{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=0),
    ),
    G.Stat(
        title="ZK: Sum of number of Alive Connections",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(zookeeper_numaliveconnections{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=0),
    ),
    G.Stat(
        title="ZK: Sum of watchers",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(zookeeper_inmemorydatatree_watchcount{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=0),
    ),
    G.TimeSeries(
        title="ZK: Outstanding Requests",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='zookeeper_outstandingrequests{namespace="$ns"}',
                legendFormat="{{pod}} ({{server_id}}:{{member_type}})",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "last"],
        legendPlacement="right",
        gridPos=G.GridPos(h=defaultHeight, w=8, x=statWidth * 4, y=0),
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
                expr='count(kafka_server_replicamanager_leadercount{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=1),
    ),
    G.Stat(
        title="Kafka: Active Controller",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_controller_kafkacontroller_activecontrollercount{namespace="$ns"} > 0',
                legendFormat="{{pod}}",
            ),
        ],
        reduceCalc="last",
        textMode="value_and_name",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=1),
    ),
    G.Stat(
        title="Kafka: Sum of Partitions",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_server_replicamanager_partitioncount{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=1),
    ),
    G.Stat(
        title="Kafka: Sum of Partitions Under-Replicated (URP)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_server_replicamanager_underreplicatedpartitions{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="green"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=1),
    ),
    G.Stat(
        title="Kafka: Sum of Partitions Under-MinISR",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_cluster_partition_underminisr{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="green"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 4, y=1),
    ),
    G.Stat(
        title="Kafka: Sum of Partitions Offline",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_controller_kafkacontroller_offlinepartitionscount{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="green"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 5, y=1),
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
                expr='count(kafka_schema_registry_registered_count{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="red"),
            G.Threshold(index=1, value=1.0, color="yellow"),
            G.Threshold(index=2, value=2.0, color="green"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=2),
    ),
    G.Stat(
        title="SR: Sum of Registered Schemas",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_schema_registry_registered_count{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=2),
    ),
    G.Stat(
        title="SR: Sum of Deleted Schemas",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_schema_registry_schemas_deleted{namespace="$ns"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=2),
    ),
]

connect_panels = [
    G.RowPanel(
        title="Kafka Connect cluster: $connect_app",
        gridPos=G.GridPos(h=1, w=24, x=0, y=3),
        repeat=G.Repeat(variable="connect_app"),
    ),
    G.Stat(
        title="Connect: Online Workers",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='count(kafka_connect_connect_worker_metrics_connector_count{namespace="$ns",app=~"$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=3),
    ),
    G.Stat(
        title="Connect: Sum of Total Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_total_task_count{namespace="$ns",app=~"$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=3),
    ),
    G.Stat(
        title="Connect: Sum of Running Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_running_task_count{namespace="$ns",app=~"$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="green"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=3),
    ),
    G.Stat(
        title="Connect: Sum of Paused Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_paused_task_count{namespace="$ns",app=~"$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="yellow"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=3),
    ),
    G.Stat(
        title="Connect: Sum of Failed Tasks",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_connect_connect_worker_metrics_connector_failed_task_count{namespace="$ns",app=~"$connect_app"})',
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
            G.Threshold(index=1, value=1.0, color="red"),
        ],
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 4, y=3),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 5, y=3),
    ),
]

ksqldb_panels = [
    G.RowPanel(
        title="ksqlDB cluster: $ksqldb_app",
        gridPos=G.GridPos(h=1, w=24, x=0, y=4),
        repeat=G.Repeat(variable="ksqldb_app"),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=4),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=4),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=4),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=4),
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
        gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 4, y=4),
    ),
]

panels = zk_panels + kafka_panels + sr_panels + connect_panels + ksqldb_panels

dashboard = G.Dashboard(
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
