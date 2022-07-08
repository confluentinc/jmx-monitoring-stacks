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
                name="broker",
                label="Broker",
                dataSource="Prometheus",
                query="label_values(kafka_server_replicamanager_leadercount{"
                + env_label
                + '="$env"}, '
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="quantile",
                label="Quantile",
                dataSource="Prometheus",
                query="label_values(kafka_network_requestmetrics_requestqueuetimems{"
                + env_label
                + '="$env"}, quantile)',
            ),
        ]
    )

    healthcheck_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=0),
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
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 1, y=0),
        ),
        G.Stat(
            title="Kafka: Sum of Replica Imbalance",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_preferredreplicaimbalancecount{"
                    + env_label
                    + '="$env"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_globaltopiccount{"
                    + env_label
                    + '="$env"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(rate(kafka_network_requestmetrics_requestspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            title="Kafka: Logs Size",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_log_log_size{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by ('
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
        G.Stat(
            title="Kafka: Sum of Partitions",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_partitioncount{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=default_height, w=stat_width, x=stat_width * 0, y=1),
        ),
        G.Stat(
            title="Kafka: Sum of Partitions Under-Replicated (URP)",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_replicamanager_underreplicatedpartitions{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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
            title="Kafka: Sum of Partitions Under-MinISR",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_cluster_partition_underminisr{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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
            title="Kafka: Sum of Partitions Offline",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_controller_kafkacontroller_offlinepartitionscount{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(rate(kafka_server_brokertopicmetrics_bytesinpersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(rate(kafka_server_brokertopicmetrics_bytesoutpersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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

    system_base = 2

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
                    + server_label
                    + '=~"$broker"}[5m])',
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
                    + server_label
                    + '=~"$broker"})',
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
                    + server_label
                    + '=~"$broker"}[5m]))',
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

    throughtput_base = system_base + 1
    throughput_inner = [
        G.TimeSeries(
            title="Messages In/Sec",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_messagesinpersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_bytesinpersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(topic) (rate(kafka_server_brokertopicmetrics_bytesoutpersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            description="Bytes in/out per second",
            gridPos=G.GridPos(h=1, w=24, x=0, y=throughtput_base),
            collapsed=True,
            panels=throughput_inner,
        ),
    ]

    thread_base = throughtput_base + 1
    thread_inner = [
        G.TimeSeries(
            title="Network processor usage",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="1-kafka_network_socketserver_networkprocessoravgidlepercent{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="1-kafka_server_kafkarequesthandlerpool_requesthandleravgidlepercent_total{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}',
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
            title="Thread Utilization",
            description="Internal thread pools usage",
            gridPos=G.GridPos(h=1, w=24, x=0, y=thread_base),
            collapsed=True,
            panels=thread_inner,
        ),
    ]

    request_base = thread_base + 1
    request_inner = [
        G.TimeSeries(
            title="Requests rates",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(pod,instance,statefulset_kubernetes_io_pod_name)(rate(kafka_network_requestmetrics_requestspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m]))',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum without(pod,instance,statefulset_kubernetes_io_pod_name)(rate(kafka_network_requestmetrics_errorspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",error!="NONE"}[5m]))',
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
            description="Sum of req/sec rates",
            gridPos=G.GridPos(h=1, w=24, x=0, y=request_base),
            collapsed=True,
            panels=request_inner,
        ),
    ]

    connection_base = request_base + 1
    connection_inner = [
        G.TimeSeries(
            title="Sum of Connections alive per Broker",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_count{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by ('
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_creation_rate{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by ('
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_close_rate{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by ('
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_count{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by (listener)',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_creation_rate{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by (listener)',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connection_close_rate{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by (listener)',
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

    isr_base = connection_base + 2
    isr_inner = [
        G.TimeSeries(
            title="Rate of ISR Shrinks/sec",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="rate(kafka_server_replicamanager_isrshrinkspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m])',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="rate(kafka_server_replicamanager_isrexpandspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}[5m])',
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

    producer_base = isr_base + 1
    producer_inner = [
        G.TimeSeries(
            title="Produce: Request Queue Time",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Produce"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Produce"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Produce"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Produce"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Produce"}',
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

    consumer_base = producer_base + 2
    consumer_inner = [
        G.TimeSeries(
            title="Fetch: Request Queue Time",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Fetch"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Fetch"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Fetch"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Fetch"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="Fetch"}',
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

    replication_base = consumer_base + 2
    replication_inner = [
        G.TimeSeries(
            title="Fetch: Request Queue Time",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_requestqueuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="FetchFollower"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_localtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="FetchFollower"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_remotetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="FetchFollower"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsequeuetimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="FetchFollower"}',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_network_requestmetrics_responsesendtimems{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker",quantile=~"$quantile",request="FetchFollower"}',
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

    group_base = replication_base + 2
    group_inner = [
        G.TimeSeries(
            title="Number of Groups per Broker",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="kafka_coordinator_group_groupmetadatamanager_numgroups{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}',
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
            title="Number of Groups per Broker",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsstable{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
                    legendFormat="stable",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupspreparingrebalance{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
                    legendFormat="preparing_rebalance",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsdead{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
                    legendFormat="dead",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupscompletingrebalance{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
                    legendFormat="completing_rebalance",
                ),
                G.Target(
                    expr="sum(kafka_coordinator_group_groupmetadatamanager_numgroupsempty{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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

    conversion_base = group_base + 1
    conversion_inner = [
        G.TimeSeries(
            title="Sum of Produce conversion rate per sec",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_brokertopicmetrics_producemessageconversionspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_brokertopicmetrics_fetchmessageconversionspersec{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr="sum(kafka_server_socketservermetrics_connections{"
                    + env_label
                    + '="$env",'
                    + server_label
                    + '=~"$broker"}) by (client_software_name,client_software_version)',
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

    panels = (
        healthcheck_panels
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

    return G.Dashboard(
        title="Kafka cluster - v2",
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


env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
dashboard = dashboard(env_label, server_label)
