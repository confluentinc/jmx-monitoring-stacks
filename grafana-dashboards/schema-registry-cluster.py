import grafanalib.core as G

defaultHeight = 5
statWidth = 4
tsWidth = 8

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

healthcheck_base = 0
healthcheck_panels = [
    G.RowPanel(
        title="Health-check",
        gridPos=G.GridPos(h=1, w=24, x=0, y=0),
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
        gridPos=G.GridPos(
            h=defaultHeight, w=statWidth, x=statWidth * 0, y=healthcheck_base
        ),
    ),
    G.Stat(
        title="SR: Sum of Registered Schemas",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='avg(kafka_schema_registry_registered_count{namespace="$ns"})',
                instant=True,
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(
            h=defaultHeight, w=statWidth, x=statWidth * 1, y=healthcheck_base
        ),
    ),
    G.Stat(
        title="SR: Sum of Created Schemas by Type",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='avg(kafka_schema_registry_schemas_created{namespace="$ns"}) by (schema_type)',
                legendFormat="{{schema_type}}",
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(
            h=defaultHeight, w=statWidth, x=statWidth * 2, y=healthcheck_base
        ),
    ),
    G.Stat(
        title="SR: Sum of Deleted Schemas by Type",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum(kafka_schema_registry_schemas_deleted{namespace="$ns"}) by (schema_type)',
                legendFormat="{{schema_type}}",
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(
            h=defaultHeight, w=statWidth, x=statWidth * 3, y=healthcheck_base
        ),
    ),
    G.Stat(
        title="SR: Sum of Active Connections",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr="sum(kafka_schema_registry_kafka_schema_registry_metrics_connection_count)",
            ),
        ],
        reduceCalc="last",
        thresholds=[
            G.Threshold(index=0, value=0.0, color="blue"),
        ],
        gridPos=G.GridPos(
            h=defaultHeight, w=statWidth, x=statWidth * 4, y=healthcheck_base
        ),
    ),
]

system_panels = [
    G.RowPanel(
        title="System",
        gridPos=G.GridPos(h=1, w=24, x=0, y=1),
    ),
    G.TimeSeries(
        title="CPU usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='irate(process_cpu_seconds_total{namespace="$ns",type="schemaregistry"}[5m])',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 0, y=1),
    ),
    G.TimeSeries(
        title="Memory usage",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(area)(jvm_memory_bytes_used{namespace="$ns",type="schemaregistry"})',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="bytes",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 1, y=1),
    ),
    G.TimeSeries(
        title="GC collection",
        dataSource="${DS_PROMETHEUS}",
        targets=[
            G.Target(
                expr='sum without(gc)(irate(jvm_gc_collection_seconds_sum{namespace="$ns",type="schemaregistry"}[5m]))',
                legendFormat="{{pod}}",
            ),
        ],
        legendDisplayMode="table",
        legendCalcs=["max", "mean", "last"],
        unit="percentunit",
        gridPos=G.GridPos(h=defaultHeight * 2, w=tsWidth, x=tsWidth * 2, y=1),
    ),
]

panels = healthcheck_panels + system_panels

dashboard = G.Dashboard(
    title="Schema Registry cluster - v2",
    description="Overview of the Schema Registry cluster",
    tags=["confluent", "schema-registry"],
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
