import os
import grafanalib.core as G


def dashboard(ds="Prometheus", env_label="namespace", server_label="pod"):
    """
    Kafka cluster dashboard
    It includes:
    - Cluster overview
    - System resources
    - Throughput
    - Thread utilization
    - Request rates
    - Connections
    - In-Sync Replicas
    - Request latency: Producer
    - Request latency: Consumer Fetch
    - Request latency: Follower Fetch
    - Group Coordinator
    - Message Conversion

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
    by_server = by_env + "," + server_label + '=~"$broker"'

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
                name="broker",
                label="Broker",
                dataSource=ds,
                query="label_values(kafka_server_replicamanager_leadercount{"
                + by_env
                + "}, "
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="quantile",
                label="Quantile",
                dataSource=ds,
                query="label_values(kafka_network_requestmetrics_requestqueuetimems{"
                + by_env
                + "}, quantile)",
            ),
        ]
    )

    # Panel groups
    ## Cluster overview:
    ### When updating descriptions on these panels, also update descriptions in confluent-platform.py
    overview_panels = [
        G.RowPanel(
            title="Cluster Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        # First group of stats
        G.Stat(
            title="Kafka: Online Brokers",
            description="""Count of brokers available (online).
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=0),
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=0),
        ),
        G.Stat(
            title="Kafka: Sum of Preferred Replica Imbalance",
            description="""
            Number of partitions where the preferred replica is not the leader.
            Usually, this number is 0.
            Restarting nodes could cause this values to change, but when reassigning happens the value stabilize.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_preferredreplicaimbalancecount{"
                    + by_env
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=0),
        ),
        G.Stat(
            title="Kafka: Sum of Topics",
            description="Number of topics in the cluster.",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_globaltopiccount{"
                    + by_env
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 3, y=1),
        ),
        G.Stat(
            title="Kafka: Rate of Requests/Sec",
            description="""Sum of requests per second rated over a 5 min. period.
            Gives an idea of the processing load in the cluster.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(rate(kafka_network_requestmetrics_requestspersec{"
                    + by_server
                    + "}[5m]))",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            format="reqps",
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=0),
        ),
        G.Stat(
            title="Kafka: Log Size",
            description="""Sum of log sizes per broker.
            This must be compared with the total storage space available in the brokers.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_log_log_size{"
                    + by_server
                    + "}) by ("
                    + server_label
                    + ")",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            reduceCalc="last",
            textMode="value_and_name",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            format="bytes",
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 5, y=0),
        ),
        # Second group of stats
        G.Stat(
            title="Kafka: Sum of Partitions",
            description="""Sum of Topic partitions across the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_partitioncount{"
                    + by_server
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
            title="Kafka: Sum of Under-Replicated Partitions (URP)",
            description="""Sum of Under-Replicated Partitions. This is caused by broker or volumes unavailable, impacting replicas to be offline, and reducing the ISR set for those partitions.
            There are transient scenarios that could lead to this number growing (e.g. broker restart), but if the number doesn't shrink in a short period of time (e.g. 1 minute), then it's recommended to alert.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_underreplicatedpartitions{"
                    + by_server
                    + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Under-MinISR Partitions",
            description="""Number of partitions where the number of replicas offline is higher than the minimum ISR configuration.
            This means partitions are not available for Producers with acks=all.
            We recommend alerting when this values is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_cluster_partition_underminisr{" + by_server + "})",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="green"),
                G.Threshold(index=1, value=1.0, color="red"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 2, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Offline Partitions",
            description="""Number of partitions where all replicas are offline.
            Producers and Consumers are affected by this condition.
            We recommend alerting when this values is higher than 0.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_offlinepartitionscount{"
                    + by_server
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
            title="Kafka: Bytes In/Sec",
            description="""Sum of bytes in per second rated over a 5 min. period.
            Gives an idea of the incoming throughput handle by the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(rate(kafka_server_brokertopicmetrics_bytesinpersec{"
                    + by_server
                    + "}[5m]))",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            format="binBps",
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 4, y=1),
        ),
        G.Stat(
            title="Kafka: Bytes Out/Sec",
            description="""Sum of bytes out per second rated over a 5 min. period.
            Gives an idea of the outgoing throughput handle by the cluster.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(rate(kafka_server_brokertopicmetrics_bytesoutpersec{"
                    + by_server
                    + "}[5m]))",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            format="binBps",
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 5, y=1),
        ),
    ]

    ## System resources:
    ### When updating descriptions on these panels, also update descriptions in other cluster dashboards
    system_base = 2
    system_panels = [
        G.RowPanel(
            title="System resources",
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

    ## Throughput:
    throughtput_base = system_base + 1
    throughput_inner = [
        G.TimeSeries(
            title="Messages In/Sec",
            description="""Number of messages into topics per second, aggregated by sum without topic.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_messagesinpersec{"
                    + by_server
                    + "}[5m]))",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="cps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=throughtput_base
            ),
        ),
        G.TimeSeries(
            title="Bytes In/Sec",
            description="""Number of bytes into topics per second, aggregated by sum without topic.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_bytesinpersec{"
                    + by_server
                    + "}[5m]))",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=throughtput_base
            ),
        ),
        G.TimeSeries(
            title="Bytes Out/Sec",
            description="""Number of bytes out of topics per second, aggregated by sum without topic.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_bytesoutpersec{"
                    + by_server
                    + "}[5m]))",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=throughtput_base
            ),
        ),
    ]
    throughput_panels = [
        G.RowPanel(
            title="Throughput",
            gridPos=G.GridPos(h=1, w=24, x=0, y=throughtput_base),
            collapsed=True,
            panels=throughput_inner,
        ),
    ]

    ## Thread utilization:
    thread_base = throughtput_base + 1
    thread_inner = [
        G.TimeSeries(
            title="Network processor usage",
            description="""Percent of time the network thread pool is used.
            It should be below 60% or the capacity of threads should be tuned or 
            the cluster scaled to cope with the load.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="1-kafka_network_socketserver_networkprocessoravgidlepercent{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=thread_base
            ),
        ),
        G.TimeSeries(
            title="Request processor (IO) usage",
            description="""Percent of time the IO thread pool is used.
            It should be below 60% or the capacity of threads should be tuned or 
            the cluster scaled to cope with the load.""",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="1-kafka_server_kafkarequesthandlerpool_requesthandleravgidlepercent_total{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=thread_base
            ),
        ),
    ]
    thread_panels = [
        G.RowPanel(
            title="Thread utilization",
            gridPos=G.GridPos(h=1, w=24, x=0, y=thread_base),
            collapsed=True,
            panels=thread_inner,
        ),
    ]

    ## Request rates:
    request_base = thread_base + 1
    ### It has the special case of aggregating across the cluster.
    ### As the number of labels is unknown and could be extended depending on the platform.
    ### At the moment includes known labels: instance, pod, and stateful_kubernetes_io_pod_name
    known_labels = "pod,instance,statefulset_kubernetes_io_pod_name"
    request_inner = [
        G.TimeSeries(
            title="Requests rates",
            description="""Requests per second rated over a 5 minutes period.
            Includes API call and version.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without("
                    + known_labels
                    + ")(rate(kafka_network_requestmetrics_requestspersec{"
                    + by_server
                    + "}[5m]))",
                    legendFormat="{{request}}(v{{version}})",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=request_base
            ),
            stacking={"mode": "normal", "group": "A"},
        ),
        G.TimeSeries(
            title="Error rates",
            description="""Request Errors per second rated over a 5 minutes period.
            Includes API call and version.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum without("
                    + known_labels
                    + ")(rate(kafka_network_requestmetrics_errorspersec{"
                    + by_server
                    + ',error!="NONE"}[5m]))',
                    legendFormat="{{error}}@{{request}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="reqps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=request_base
            ),
            stacking={"mode": "normal", "group": "A"},
        ),
    ]
    request_panels = [
        G.RowPanel(
            title="Request rates",
            gridPos=G.GridPos(h=1, w=24, x=0, y=request_base),
            collapsed=True,
            panels=request_inner,
        ),
    ]

    ## Connections:
    connection_base = request_base + 1
    connection_inner = [
        G.TimeSeries(
            title="Sum of Connections alive per Broker",
            description="Sum of connections count across cluster by brokers",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_count{"
                    + by_server
                    + "}) by ("
                    + server_label
                    + ")",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=connection_base
            ),
        ),
        G.TimeSeries(
            title="Sum of Connections creation rate per Broker",
            description="Sum of rate of connections created across cluster by brokers",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_creation_rate{"
                    + by_server
                    + "}) by ("
                    + server_label
                    + ")",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=connection_base
            ),
        ),
        G.TimeSeries(
            title="Sum of Connections close rate per Broker",
            description="Sum of rate of connections closed across cluster by brokers",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_close_rate{"
                    + by_server
                    + "}) by ("
                    + server_label
                    + ")",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=connection_base
            ),
        ),
        # By Listener
        G.TimeSeries(
            title="Sum of Connections alive per Listener",
            description="Sum of connections count across cluster by listeners",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_count{"
                    + by_server
                    + "}) by (listener)",
                    legendFormat="{{listener}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=connection_base + 1
            ),
        ),
        G.TimeSeries(
            title="Sum of Connections creation rate per Listener",
            description="Sum of rate of connections created across cluster by listener",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_creation_rate{"
                    + by_server
                    + "}) by (listener)",
                    legendFormat="{{listener}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=connection_base + 1
            ),
        ),
        G.TimeSeries(
            title="Sum of Connections close rate per Listener",
            description="Sum of rate of connections closed across cluster by listener",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_close_rate{"
                    + by_server
                    + "}) by (listener)",
                    legendFormat="{{listener}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=connection_base + 1
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

    ## In-Sync Replicas:
    isr_base = connection_base + 2
    isr_inner = [
        G.TimeSeries(
            title="Rate of ISR Shrinks/sec",
            description="""Rate of ISR shrinks per second.
            If this value is continuously higher than 0, then troubleshoot cause of ISR changing constantly.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="rate(kafka_server_replicamanager_isrshrinkspersec{"
                    + by_server
                    + "}[5m])",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=isr_base
            ),
        ),
        G.TimeSeries(
            title="Rate of ISR Expands/sec",
            description="""Rate of ISR expands per second.
            If this value is continuously higher than 0, then troubleshoot cause of ISR changing constantly.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="rate(kafka_server_replicamanager_isrexpandspersec{"
                    + by_server
                    + "}[5m])",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=isr_base
            ),
        ),
    ]
    isr_panels = [
        G.RowPanel(
            title="In-Sync Replicas",
            gridPos=G.GridPos(h=1, w=24, x=0, y=isr_base),
            collapsed=True,
            panels=isr_inner,
        ),
    ]

    ## Request latency for Produce:
    ### When changing these panels, also modify Consumer Fetch and Follower Fetch.
    producer_base = isr_base + 1
    producer_inner = [
        G.TimeSeries(
            title="Produce: Request Queue Time",
            description="""Time expend on the request queue.
            Moved from network socket to request queue by Network threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Produce"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=producer_base
            ),
        ),
        G.TimeSeries(
            title="Produce: Local Time",
            description="""Time expend doing local IO.
            Moved from request queue to storage device operations by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Produce"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=producer_base
            ),
        ),
        G.TimeSeries(
            title="Produce: Remote Time",
            description="""Time expend waiting for coordination with other brokers/internal condition.
            At purgatory.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Produce"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=producer_base
            ),
        ),
        G.TimeSeries(
            title="Produce: Response Queue Time",
            description="""Time expend waiting in response queue.
            Moved from purgatory to response queue by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Produce"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=producer_base + 1
            ),
        ),
        G.TimeSeries(
            title="Produce: Response Send Time",
            description="""Time expend delivering response.
            Moved from response queue to client by Networkc threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Produce"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=producer_base + 1
            ),
        ),
    ]
    producer_panels = [
        G.RowPanel(
            title="Request latency: Producer",
            gridPos=G.GridPos(h=1, w=24, x=0, y=producer_base),
            collapsed=True,
            panels=producer_inner,
        ),
    ]

    ## Request latency for Consumer Fetch:
    ### When changing these panels, also modify Produce and Follower Fetch.
    consumer_base = producer_base + 2
    consumer_inner = [
        G.TimeSeries(
            title="Fetch: Request Queue Time",
            description="""Time expend on the request queue.
            Moved from network socket to request queue by Network threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Fetch"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=consumer_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Local Time",
            description="""Time expend doing local IO.
            Moved from request queue to storage device operations by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Fetch"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=consumer_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Remote Time",
            description="""Time expend waiting for coordination with other brokers/internal condition.
            At purgatory.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Fetch"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=consumer_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Response Queue Time",
            description="""Time expend waiting in response queue.
            Moved from purgatory to response queue by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Fetch"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=consumer_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch: Response Send Time",
            description="""Time expend delivering response.
            Moved from response queue to client by Networkc threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="Fetch"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=consumer_base + 1
            ),
        ),
    ]
    consumer_panels = [
        G.RowPanel(
            title="Request latency: Consumer Fetch",
            gridPos=G.GridPos(h=1, w=24, x=0, y=consumer_base),
            collapsed=True,
            panels=consumer_inner,
        ),
    ]

    ## Request latency for Follower Fetch:
    ### When changing these panels, also modify Produce and Consumer Fetch.
    replication_base = consumer_base + 2
    replication_inner = [
        G.TimeSeries(
            title="Fetch: Request Queue Time",
            description="""Time expend on the request queue.
            Moved from network socket to request queue by Network threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="FetchFollower"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=replication_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Local Time",
            description="""Time expend doing local IO.
            Moved from request queue to storage device operations by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="FetchFollower"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=replication_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Remote Time",
            description="""Time expend waiting for coordination with other brokers/internal condition.
            At purgatory.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="FetchFollower"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=replication_base
            ),
        ),
        G.TimeSeries(
            title="Fetch: Response Queue Time",
            description="""Time expend waiting in response queue.
            Moved from purgatory to response queue by IO threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="FetchFollower"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=replication_base + 1
            ),
        ),
        G.TimeSeries(
            title="Fetch: Response Send Time",
            description="""Time expend delivering response.
            Moved from response queue to client by Networkc threads.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + by_server
                    + ',quantile=~"$quantile",request="FetchFollower"}',
                    legendFormat="{{" + server_label + "}} ({{quantile}}th)",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=replication_base + 1
            ),
        ),
    ]
    replication_panels = [
        G.RowPanel(
            title="Request latency: Replica Fetch",
            gridPos=G.GridPos(h=1, w=24, x=0, y=replication_base),
            collapsed=True,
            panels=replication_inner,
        ),
    ]

    ## Group Coordination:
    group_base = replication_base + 2
    group_inner = [
        G.TimeSeries(
            title="Number of Groups per Broker",
            description="Number of groups managed by Broker",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="kafka_coordinator_group_groupmetadatamanager_numgroups{"
                    + by_server
                    + "}",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=group_base
            ),
        ),
        G.TimeSeries(
            title="Number of Groups per Broker per Status",
            description="Number of stable groups managed by Broker",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsstable{"
                    + by_server
                    + "})",
                    legendFormat="stable",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupspreparingrebalance{"
                    + by_server
                    + "})",
                    legendFormat="preparing_rebalance",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsdead{"
                    + by_server
                    + "})",
                    legendFormat="dead",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupscompletingrebalance{"
                    + by_server
                    + "})",
                    legendFormat="completing_rebalance",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsempty{"
                    + by_server
                    + "})",
                    legendFormat="empty",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            stacking={"mode": "normal"},
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=group_base
            ),
        ),
    ]
    group_panels = [
        G.RowPanel(
            title="Group Coordinator",
            gridPos=G.GridPos(h=1, w=24, x=0, y=group_base),
            collapsed=True,
            panels=group_inner,
        ),
    ]

    ## Conversion:
    conversion_base = group_base + 1
    conversion_inner = [
        G.TimeSeries(
            title="Sum of Produce conversion rate per sec",
            description="""Sum of produce message conversions per second.
            This value increases when the broker receives produce messages from clients using older versions.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_brokertopicmetrics_producemessageconversionspersec{"
                    + by_server
                    + "})",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="opsps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 0, y=conversion_base
            ),
        ),
        G.TimeSeries(
            title="Sum of Fetch conversion rate per sec",
            description="""Sum of fetch message conversions per second.
            This value increases when the broker receives fetch messages from clients using older versions.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_brokertopicmetrics_fetchmessageconversionspersec{"
                    + by_server
                    + "})",
                    legendFormat="{{" + server_label + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="opsps",
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 1, y=conversion_base
            ),
        ),
        G.TimeSeries(
            title="Sum of Connections per version",
            description="""Sum of connections aggregated by client version and name.
            """,
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connections{"
                    + by_server
                    + "}) by (client_software_name,client_software_version)",
                    legendFormat="{{client_software_name}} (v{{client_software_version}})",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            gridPos=G.GridPos(
                h=default_height * 2, w=ts_width, x=ts_width * 2, y=conversion_base
            ),
        ),
    ]
    conversion_panels = [
        G.RowPanel(
            title="Message Conversion",
            gridPos=G.GridPos(h=1, w=24, x=0, y=conversion_base),
            collapsed=True,
            panels=conversion_inner,
        ),
    ]

    # group all panels
    panels = (
        overview_panels
        + system_panels
        + throughput_panels
        + thread_panels
        + request_panels
        + connection_panels
        + isr_panels
        + producer_panels
        + consumer_panels
        + replication_panels
        + group_panels
        + conversion_panels
    )

    # build dashboard
    return G.Dashboard(
        title="Kafka cluster",
        description="Overview of the Kafka cluster",
        tags=["confluent", "kafka"],
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

# dashboard required by grafanalib
dashboard = dashboard(ds, env_label, server_label)
