from grafanalib.core import (
    Dashboard, TimeSeries, GaugePanel,
    Target, GridPos, Row,
    OPS_FORMAT
)

panels = [
        TimeSeries(
            title="Random Walk",
            dataSource='default',
            targets=[
                Target(
                    datasource='grafana',
                    expr='example',
                ),
            ],
            gridPos=GridPos(h=8, w=16, x=0, y=0),
        ),
        GaugePanel(
            title="Random Walk",
            dataSource='default',
            targets=[
                Target(
                    datasource='grafana',
                    expr='example',
                ),
            ],
            gridPos=GridPos(h=4, w=4, x=17, y=0),
        ),
        TimeSeries(
            title="Prometheus http requests",
            dataSource='prometheus',
            targets=[
                Target(
                    expr='rate(prometheus_http_requests_total[5m])',
                    legendFormat="{{ handler }}",
                    refId='A',
                ),
            ],
            unit=OPS_FORMAT,
            gridPos=GridPos(h=8, w=16, x=0, y=10),
        ),
    ]

dashboard = Dashboard(
    title="Confluent Platform overview - v2",
    description="Overview of the main health-check metrics from Confluent Platform components.",
    tags=[
        'confluent', 'kafka', 'zookeeper', 'kafka-connect', 'schema-registry', 'ksqldb'
    ],
    timezone="browser",
    rows=[Row(title='Zookeeper',showTitle=True,panels=panels)],
).auto_panel_ids()
