import grafanalib.core as G

defaultHeight=5
statWidth=4

panels = [
        G.RowPanel(
            title='Zookeeper',
            gridPos=G.GridPos(h=1, w=24, x=0, y=0),
        ),
        G.Stat(
            title="ZK: Quorum Size",
            dataSource='${DS_PROMETHEUS}',
            targets=[
                G.Target(
                    expr='count(zookeeper_status_quorumsize{namespace="$ns"})',
                ),
            ],
            thresholds=[
              G.Threshold(index=0, value=0.0, color="red"),
              G.Threshold(index=1, value=2.0, color="yellow"),
              G.Threshold(index=2, value=3.0, color="green"),
            ],
            gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 0, y=0),
        ),
        G.Stat(
            title="ZK: Avg. number of ZNodes",
            dataSource='${DS_PROMETHEUS}',
            targets=[
                G.Target(
                    expr='avg(zookeeper_inmemorydatatree_nodecount{namespace="$ns"})',
                ),
            ],
            thresholds=[
              G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 1, y=0),
        ),
        G.Stat(
            title="ZK: Sum of number of Alive Connections",
            dataSource='${DS_PROMETHEUS}',
            targets=[
                G.Target(
                    expr='sum(zookeeper_numaliveconnections{namespace="$ns"})',
                ),
            ],
            thresholds=[
              G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 2, y=0),
        ),
        G.Stat(
            title="ZK: Sum of watchers",
            dataSource='${DS_PROMETHEUS}',
            targets=[
                G.Target(
                    expr='sum(zookeeper_inmemorydatatree_watchcount{namespace="$ns"})',
                ),
            ],
            thresholds=[
              G.Threshold(index=0, value=0.0, color="blue"),
            ],
            gridPos=G.GridPos(h=defaultHeight, w=statWidth, x=statWidth * 3, y=0),
        ),
        G.TimeSeries(
            title="ZK: Outstanding Requests",
            dataSource='${DS_PROMETHEUS}',
            targets=[
                G.Target(
                    expr='zookeeper_outstandingrequests{namespace="$ns"}',
                    legendFormat="{{pod}}",
                ),
            ],
            legendDisplayMode="table",
            legendCalcs=["max","last"],
            legendPlacement="right",
            gridPos=G.GridPos(h=defaultHeight, w=8, x=statWidth * 4, y=0),
        ),
    ]

dashboard = G.Dashboard(
    title="Confluent Platform overview - v2",
    description="Overview of the main health-check metrics from Confluent Platform components.",
    tags=[
        'confluent', 'kafka', 'zookeeper', 'kafka-connect', 'schema-registry', 'ksqldb'
    ],
    inputs=[G.DataSourceInput(name="DS_PROMETHEUS",label="Prometheus",pluginId="prometheus",pluginName="Prometheus")],
    templating=G.Templating(list=[G.Template(name='ns',label='Namespace',dataSource='Prometheus',query='label_values(namespace)')]),
    timezone="browser",
    panels=panels,
).auto_panel_ids()
