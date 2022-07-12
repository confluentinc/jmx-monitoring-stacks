import os
import grafanalib.core as G


def dashboard(ds="Prometheus", env_label="namespace", server_label="pod"):
    """
    Schema Registry cluster dashboard
    It includes:
    - Cluster overview
    - System resources

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
    by_server = by_env + "," + server_label + '="$sr_server"'

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
                name="sr_server",
                label="Server",
                dataSource=ds,
                query="label_values(kafka_schema_registry_registered_count{"
                + by_env
                + "}, "
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    # Panel groups
    ## Cluster overview:
    ### When updating descriptions on these panels, also update descriptions in confluent-platform.py
    healthcheck_base = 0
    healthcheck_panels = [
        G.RowPanel(
            title="Overview",
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
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
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 0, y=healthcheck_base
            ),
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
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 1, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Created Schemas by Type (avg.)",
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
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 2, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Sum of Deleted Schemas by Type",
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
            gridPos=G.GridPos(
                h=default_height, w=stat_width, x=stat_width * 3, y=healthcheck_base
            ),
        ),
        G.Stat(
            title="SR: Sum of Active Connections",
            description="Number of active connections",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="sum(kafka_schema_registry_kafka_schema_registry_metrics_connection_count{"
                    + by_env
                    + "})",
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

    ## System resources:
    system_panels = [
        G.RowPanel(
            title="System",
            gridPos=G.GridPos(h=1, w=24, x=0, y=1),
        ),
        G.TimeSeries(
            title="CPU usage",
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
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=1),
        ),
        G.TimeSeries(
            title="Memory usage",
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
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=1),
        ),
        G.TimeSeries(
            title="GC collection",
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
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=1),
        ),
    ]

    # group all panels
    panels = healthcheck_panels + system_panels

    # build dashboard
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


# main labels to customize dashboard
ds = os.environ.get("DATASOURCE", "Prometheus")
env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")

# dashboard required by grafanalib
dashboard = dashboard(ds, env_label, server_label)
