import os
import grafanalib.core as G

def dashboard(env_label='namespace',server_label='pod'):
    default_height = 5
    stat_width = 4
    ts_width = 8
    
    templating = G.Templating(
        list=[
            G.Template(
                name="env",
                label="Environment",
                dataSource="Prometheus",
                query="label_values("+env_label+")",
            ),
            G.Template(
                name="sr_server",
                label="Server",
                dataSource="Prometheus",
                query="label_values(kafka_schema_registry_registered_count{"
                + env_label
                + '="$env"}, '
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
        ]
    )
    
    healthcheck_base = 0
    healthcheck_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="SR: Online instances",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='count(kafka_schema_registry_registered_count{' + env_label + '="$env"})',
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="red"),
                G.Threshold(index=1, value=1.0, color="yellow"),
                G.Threshold(index=2, value=2.0, color="green"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 0, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Sum of Registered Schemas",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='avg(kafka_schema_registry_registered_count{' + env_label + '="$env"})',
                    instant=True,
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 1, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Sum of Created Schemas by Type",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='avg(kafka_schema_registry_schemas_created{' + env_label + '="$env"}) by (schema_type)',
                    legendFormat="{{schema_type}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 2, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Sum of Deleted Schemas by Type",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='sum(kafka_schema_registry_schemas_deleted{' + env_label + '="$env"}) by (schema_type)',
                    legendFormat="{{schema_type}}",
                ),
            ],
            reduceCalc="last",
            thresholds=[
                G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 3, y=healthcheck_base
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
                h=default_height, w=stat_width, x=stat_width * 4, y=healthcheck_base
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
                    expr='irate(process_cpu_seconds_total{' + env_label + '="$env",'+server_label+'=~"$sr_server"}[5m])',
                    legendFormat="{{"+server_label+"}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=1),
        ),
        G.TimeSeries(
            title="Memory usage",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='sum without(area)(jvm_memory_bytes_used{' + env_label + '="$env",'+server_label+'=~"$sr_server"})',
                    legendFormat="{{"+server_label+"}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="bytes",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=1),
        ),
        G.TimeSeries(
            title="GC collection",
            dataSource="${DS_PROMETHEUS}",
            targets=[
                G.Target(
                    expr='sum without(gc)(irate(jvm_gc_collection_seconds_sum{' + env_label + '="$env",'+server_label+'=~"$sr_server"}[5m]))',
                    legendFormat="{{"+server_label+"}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percentunit",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=1),
        ),
    ]
    
    panels = healthcheck_panels + system_panels
    
    return G.Dashboard(
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

env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
dashboard = dashboard(env_label, server_label)
