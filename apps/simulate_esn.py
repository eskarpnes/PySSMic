import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

from app import app


def get_df():
    return pd.DataFrame({'c1': [384, 827], 'c2': [848, 874]})


def energy_use(df):
    df_sum = df.sum(axis=1)
    n = 100/(df_sum[0]+df_sum[1])
    return (
        html.H1("Energy use"),
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Pie(
                        values=[df_sum[0]*n, df_sum[1]*n],
                        labels=["Local", "Not local"]
                    )
                ]
            )
        )
    )


layout = (
    html.Div(
        energy_use(get_df())
    )
)


