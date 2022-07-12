import os
import grafanalib.core as G


def dashboard(env_label="namespace", server_label="pod"):
    default_height = 6
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
                query="label_values(kafka_server_produce_byte_rate{"
                + env_label
                + '="$env"},'
                + server_label
                + ")",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="user",
                label="User",
                dataSource="Prometheus",
                query="label_values(user)",
                multi=True,
                includeAll=True,
            ),
            G.Template(
                name="client_id",
                label="Client ID",
                dataSource="Prometheus",
                query="label_values(client_id)",
                multi=True,
                includeAll=True,
            ),
        ]
    )

    topk = "10"

    panels = [
        G.TimeSeries(
            title="Produce Byte Rate",
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_produce_byte_rate{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_fetch_byte_rate{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_request_request_time{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"})',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_produce_throttle_time{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"} > 0)',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_fetch_throttle_time{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"} > 0)',
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
            dataSource="Prometheus",
            targets=[
                G.Target(
                    expr="topk("
                    + topk
                    + ",kafka_server_request_throttle_time{"
                    + env_label
                    + '="$env",user=~"$user",client_id=~"$client_id", '
                    + server_label
                    + '=~"$broker"} > 0)',
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
        title="Kafka Quotas - v2",
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


env_label = os.environ.get("ENV_LABEL", "env")
server_label = os.environ.get("SERVER_LABEL", "hostname")
dashboard = dashboard(env_label, server_label)
