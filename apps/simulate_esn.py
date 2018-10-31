import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
import dash_table_experiments as dt
import plotly.graph_objs as go
import json
import pandas as pd
from app import app
import pickle

"""-------------------------ENERGY USE-------------------------"""


def get_energy_df():
    return pd.DataFrame({'c1': [384, 827], 'c2': [848, 874]})


def energy_use():
    #df_sum = df.sum(axis=1)
    #n = 100 / grid + pv
    return (
        dcc.Graph(
            id="energy-use-graph",
            figure=go.Figure(
                data=[
                    go.Pie(
                        #values=[df_sum[0] * n, df_sum[1] * n],
                        values=[50, 50],
                        labels=["Local", "Not local"]
                    )
                ]
            )
        )
    )


""""-------------------------CONTRACT OVERVIEW-------------------------"""


def contract_overview():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                "id", "time_of_agreement", "job_id", "producer_id"],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="contract-table"
        )
    )


"""-------------------------AVAILABLE VS USED ENERGY-------------------------"""


def get_consumption():
    return


def energy_consumption():
    return (
        dcc.Graph(
            id="energy-consumption-graph",
            figure=go.Figure(
                data=[
                    # TODO: Update to input values from simulator in 'get_consumption()'
                    go.Scatter(
                        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                        y=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                        name="Energy used"
                    ),
                    go.Scatter(
                        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                        y=[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                        name="Energy available"
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


def get_dropdown_options():
    print("Loading options")
    options = []
    for root, dirnames, filenames in os.walk("results"):
        for filename in filenames:
            if filename.endswith('.pkl'):
                options.append({
                    "label": filename[:-4], "value": filename}
                )
    if not options:
        options.append({"label": "No results saved.", "value": []})
    return options


"""-------------------------LAYOUT-------------------------"""


layout = html.Div(children=[
    dcc.Dropdown(
        id="result",
        options=get_dropdown_options(),
        value=get_dropdown_options()[0]["value"]
    ),
    html.Button('Update results', className='btn', id='btn-update'),
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='All households', children=[
            html.Div(
                html.H2("Energy use")
            ),
            html.Div([
                energy_use()
            ], className="pie-chart"),

            html.Div(
                html.H2("Contracts")
            ),
            html.Div([
                contract_overview()
            ], className="contract-table"),

            html.Div(
                html.H2("Available vs Used energy")
            ),
            html.Div([
                energy_consumption()
            ], className="consumption-graph"),
            html.Button("Start simulation", id="btnSimulationStart")
        ]),
        dcc.Tab(label='One household', children=[
            # TODO
        ]),
        dcc.Tab(label='All simulations', children=[
            # TODO
        ])
    ])
])


"""-------------------------APP CALLBACKS-------------------------"""


# @app.callback(Output("contract-table", "rows"),
#               [Input("btnSimulationStart", "n_clicks"),
#                Input('datatableDiv', 'children')])
# def update_table(n, children):
#     if n and n > 0:
#         return json.loads(children)


@app.callback(Output("result", "options"),
              [Input("btn-update", "n_clicks")])
def update_dropdown(n_clicks):
    print("click")
    return get_dropdown_options()


@app.callback(Output("contract-table", "rows"),
              [Input("result", "value")])
def update_contracts(value):
    contracts = open_file(value)[0]
    contracts = pd.DataFrame(contracts)
    rows = []
    run = 0 #TODO: Exchange with chosen simulation (currently chooses first simulation)
    for e in range(0, len(contracts)):
        rows.append(contracts[e][run])
    return rows


@app.callback(Output("energy-use-graph", "values"),
              [Input("result", "value")])
def update_pie_chart(value):
    return [30, 70]


"""-------------------------HELPING METHODS-------------------------"""


def open_file(file_name):
    with open('./results/{}'.format(file_name), 'rb') as f:
        res = pickle.load(f)
        contracts = res[0]
        profiles = res[1]
    return contracts, profiles





