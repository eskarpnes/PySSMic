import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd


from app import app

"""-------------------------ENERGY USE-------------------------"""


def get_energy_df():
    return pd.DataFrame({'c1': [384, 827], 'c2': [848, 874]})


def energy_use(df):
    df_sum = df.sum(axis=1)
    n = 100/(df_sum[0]+df_sum[1])
    return (
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


""""-------------------------CONTRACT OVERVIEW-------------------------"""


def get_contracts():
    return {"Contract ID": [1], "Contract signed (time)": [12.32], "Start of contract (time)": [14.55], "Consumer": ["c1"], "Producer": ["p1"]}


def contract_overview(records):
    return (
        dt.DataTable(
            rows=[records],
            columns=["Contract ID", "Contract signed (time)", "Start of contract (time)", "Consumer", "Producer"],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="datatable"
        )
    )


"""-------------------------AVAILABLE VS USED ENERGY-------------------------"""


def get_consumption():
    return


def energy_consumption():
    return (
        dcc.Graph(
            figure=go.Figure(
                data=[
                    #TODO: Update to input values from simulator
                    go.Scatter(
                        x=[1, 2, 3, 4], y=[4, 3, 2, 1],
                        name="Energy available"
                    ),
                    go.Scatter(
                        x=[4, 3, 2, 1], y=[3, 3, 3, 3],
                        name="Energy used"
                    )
                ],
                layout=go.Layout(
                    xaxis={
                        'title': 'Time'
                    },
                    yaxis={
                        'title': 'Energy'
                    }
                )
            )
        )
    )


"""-------------------------LAYOUT-------------------------"""
layout = html.Div([
    html.Div(
        html.H2("Energy use")
    ),
    html.Div(
        energy_use(get_energy_df())
    ),
    html.Div(
        html.H2("Contracts")
    ),
    html.Div(
        contract_overview(get_contracts())
    ),
    html.Div(
        html.H2("Available vs Used energy")
    ),
    html.Div(
        #energy_consumption()
        #TODO: Fix that consumption don't overwrite pie chart when uncommented
    )
])



