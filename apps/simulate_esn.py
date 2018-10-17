import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from app import app

layout = html.Div(children=[
    html.H1("This is a pie chart"),
    dcc.Graph(
        figure=go.Figure(
            data=[
                go.Pie(
                    values=[1, 2, 3],
                    labels=["1", "2", "3"]
                )
            ]
        )
    )
])
