import os
import grafanalib.core as G


def dashboard(ds="Prometheus", env_label="namespace", server_label="pod"):
    """
    Kafka Quotas dashboard
    It includes:
    - Quotas overview
    - Throttling

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
    default_height = 6
    ts_width = 8
    topk = "10"

    # Queries
    by_env = env_label + '="$env"'
    by_client = (
        by_env
        + ',user=~"$user",client_id=~"$client_id",'
        + server_label
        + '=~"$broker"'
    )

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
                query="label_values(kafka_server_produce_byte_rate{"
                + by_env
                + "},"
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="user",
                label="User",
                dataSource=ds,
                query="label_values(user)",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="client_id",
                label="Client ID",
                dataSource=ds,
                query="label_values(client_id)",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    # Panels:
    panels = [
        G.TimeSeries(
            title="Produce Byte Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_produce_byte_rate{"
                    + by_client
                    + "})",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=0),
        ),
        G.TimeSeries(
            title="Fetch Byte Rate",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_fetch_byte_rate{"
                    + by_client
                    + "})",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="binBps",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=0),
        ),
        G.TimeSeries(
            title="Request Time",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_request_request_time{"
                    + by_client
                    + "})",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="percent",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=0),
        ),
        G.TimeSeries(
            title="Produce Throttle Time",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_produce_throttle_time{"
                    + by_client
                    + "} > 0)",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 0, y=1),
        ),
        G.TimeSeries(
            title="Fetch Throttle Time",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_fetch_throttle_time{"
                    + by_client
                    + "} > 0)",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 1, y=1),
        ),
        G.TimeSeries(
            title="Request Throttle Time",
            dataSource=ds,
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_request_throttle_time{"
                    + by_client
                    + "} > 0)",
                    legendFormat="User:{{user}} | Client ID:{{client_id}} @ Broker:{{"
                    + server_label
                    + "}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max", "mean", "last"],
            unit="ms",
            gridPos=G.GridPos(h=default_height * 2, w=ts_width, x=ts_width * 2, y=1),
        ),
    ]

    return G.Dashboard(
        title="Kafka Quotas",
        description="Overview of the Kafka quotass",
        tags=["confluent", "kafka-client", "kafka-quota"],
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
