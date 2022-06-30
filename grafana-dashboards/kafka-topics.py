import grafanalib.core as G

defaultHeight = 10
tsWidth = 12
tableWidth = 12

templating = G.Templating(
    list=[
        G.Template(
            name="ns",
            label="Namespace",
            dataSource="Prometheus",
            query="label_values(namespace)",
        ),
        G.Template(
            name="topic",
            label="Topic",
            dataSource="Prometheus",
            query='label_values(kafka_log_log_size{namespace="$ns"}, topic)',
            multi=True,
            includeAll=True,
        ),
    ]
)

topk = "10"

throughput_base = 0
throughput_layers = 3
throughput_panels = [
    G.RowPanel(
        title="Throughput",
        gridPos=G.GridPos(h=1, w=24, x=0, y=throughput_base),
    ),
    G.TimeSeries(
        title="Messages In/Sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum without(instance,pod,statefulset_kubernetes_io_pod_name) (rate(kafka_server_brokertopicmetrics_messagesinpersec{topic=~"$topic",namespace="$ns"}[5m])))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="cps",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(h=defaultHeight, w=tsWidth, x=tsWidth * 0, y=throughput_base),
    ),
    G.TimeSeries(
        title="Log size",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum(kafka_log_log_size{namespace="$ns",topic=~"$topic"}) by (topic))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(h=defaultHeight, w=tsWidth, x=tsWidth * 1, y=throughput_base),
    ),
    G.TimeSeries(
        title="Bytes In/Sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum without(instance,pod,statefulset_kubernetes_io_pod_name) (rate(kafka_server_brokertopicmetrics_bytesinpersec{topic=~"$topic",namespace="$ns"}[5m])))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="binBps",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(
            h=defaultHeight, w=tsWidth, x=tsWidth * 0, y=throughput_base + 1
        ),
    ),
    G.TimeSeries(
        title="Bytes Out/Sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum without(instance,pod,statefulset_kubernetes_io_pod_name) (rate(kafka_server_brokertopicmetrics_bytesoutpersec{topic=~"$topic",namespace="$ns"}[5m])))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="binBps",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(
            h=defaultHeight, w=tsWidth, x=tsWidth * 1, y=throughput_base + 1
        ),
    ),
    G.TimeSeries(
        title="Produce Requests/Sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum(rate(kafka_server_brokertopicmetrics_totalproducerequestspersec{ namespace="$ns", topic=~"$topic"}[5m])) by (topic))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="reqps",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(
            h=defaultHeight, w=tsWidth, x=tsWidth * 0, y=throughput_base + 2
        ),
    ),
    G.TimeSeries(
        title="Consumer Fetch Requests/Sec",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="topk("
                + topk
                + ', sum(rate(kafka_server_brokertopicmetrics_totalfetchrequestspersec{ namespace="$ns", topic=~"$topic"}[5m])) by (topic))',
                legendFormat="{{topic}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="reqps",
        stacking={"mode": "normal"},
        gridPos=G.GridPos(
            h=defaultHeight, w=tsWidth, x=tsWidth * 1, y=throughput_base + 2
        ),
    ),
]


offsets_txs = [
    {
        "id": "organize",
        "options": {
            "excludeByName": {
                "Time": True,
                "__name__": True,
                "app": True,
                "confluent_platform": True,
                "controller_revision_hash": True,
                "job": True,
                "clusterId": True,
                "confluentPlatform": True,
                "instance": True,
                "namespace": True,
                "platform_confluent_io_type": True,
                "statefulset_kubernetes_io_pod_name": True,
                "type": True,
            },
            "indexByName": {
                "pod": 1,
                "topic": 2,
                "partition": 3,
                "Value": 4,
            },
            "renameByName": {"Value": "offset"},
        },
    },
    {
        "id": "convertFieldType",
        "options": {
            "conversions": [{"destinationType": "number", "targetField": "partition"}],
            "fields": {},
        },
    },
    {"id": "sortBy", "options": {"fields": {}, "sort": [{"field": "topic"}]}},
    {
        "id": "sortBy",
        "options": {"fields": {}, "sort": [{"field": "partition"}]},
    },
]

offsets_base = throughput_base + throughput_layers
offsets_inner = [
    G.Table(
        title="Start Offsets",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_log_log_logstartoffset{namespace="$ns",topic=~"$topic"}',
                legendFormat="{{topic}}",
                format="table",
                instant=True,
            ),
        ],
        filterable=True,
        transformations=offsets_txs,
        gridPos=G.GridPos(h=defaultHeight, w=tableWidth, x=tableWidth * 0, y=offsets_base),
    ),
    G.Table(
        title="End Offsets",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='kafka_log_log_logendoffset{namespace="$ns",topic=~"$topic"}',
                legendFormat="{{topic}}",
                format="table",
                instant=True,
            ),
        ],
        filterable=True,
        transformations=offsets_txs,
        gridPos=G.GridPos(h=defaultHeight, w=tableWidth, x=tableWidth * 1, y=offsets_base),
    ),
]
offsets_panels = [
    G.RowPanel(
        title="Offsets",
        gridPos=G.GridPos(h=1, w=24, x=0, y=offsets_base),
        collapsed=True,
        panels=offsets_inner,
    ),
]

panels = throughput_panels + offsets_panels
dashboard = G.Dashboard(
    title="Kafka topics - v2",
    description="Overview of the Kafka topics",
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
