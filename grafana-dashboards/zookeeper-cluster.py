import grafanalib.core as G

hcHeight = 5
statWidth = 4
tsWidth=8

templating = G.Templating(
    list=[
        G.Template(
            name="ns",
            label="Namespace",
            dataSource="Prometheus",
            query="label_values(namespace)",
        ),
    ]
)

healthcheck_panels = [
    G.RowPanel(
        title="Health-check",
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
        gridPos=G.GridPos(h=hcHeight, w=statWidth, x=statWidth * 0, y=0),
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
        gridPos=G.GridPos(h=hcHeight, w=statWidth, x=statWidth * 1, y=0),
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
        gridPos=G.GridPos(h=hcHeight, w=statWidth, x=statWidth * 2, y=0),
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
        gridPos=G.GridPos(h=hcHeight, w=statWidth, x=statWidth * 3, y=0),
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
        gridPos=G.GridPos(h=hcHeight, w=tsWidth, x=statWidth * 4, y=0),
    ),
]

system_panels = [
    G.RowPanel(
        title="System",
        gridPos=G.GridPos(h=1, w=24, x=0, y=1),
    ),
    G.TimeSeries(
        title="ZK: CPU usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='irate(process_cpu_seconds_total{namespace="$ns",type="zookeeper"}[5m])',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*0, y=1),
    ),
    G.TimeSeries(
        title="ZK: Memory usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(area)(jvm_memory_bytes_used{namespace="$ns",type="zookeeper"})',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*1, y=1),
    ),
    G.TimeSeries(
        title="ZK: GC collection",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(gc)(irate(jvm_gc_collection_seconds_sum{namespace="$ns",type="zookeeper"}[5m]))',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*2, y=1),
    ),
]

# TODO: validate if latency metrics make sense.
# Values are high-watermark of the metric and multiplied by tick-time to represent milliseconds.
latency=[
    G.TimeSeries(
        title="ZK: Request Latency (Minimum)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='zookeeper_minrequestlatency{namespace="$ns"} * zookeeper_ticktime',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*0, y=2),
    ),
    G.TimeSeries(
        title="ZK: Request Latency (Average)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='zookeeper_avgrequestlatency{namespace="$ns"} * zookeeper_ticktime',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*1, y=2),
    ),
    G.TimeSeries(
        title="ZK: Request Latency (Maximum)",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='zookeeper_maxrequestlatency{namespace="$ns"} * zookeeper_ticktime',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="ms",
        gridPos=G.GridPos(h=hcHeight*2, w=tsWidth, x=tsWidth*2, y=2),
    ),

]
latency_panels = [
    G.RowPanel(
        title="Latency",
        gridPos=G.GridPos(h=1, w=24, x=0, y=2),
        collapsed=True,
        panels=latency
    ),
]

panels = healthcheck_panels + system_panels + latency_panels

dashboard = G.Dashboard(
    title="Zookeeper cluster - v2",
    description="Overview of the Zookeeper cluster",
    tags=["confluent", "kafka", "zookeeper"],
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
    refresh='30s',
).auto_panel_ids()
