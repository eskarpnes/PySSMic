import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from app import app
import re
import data_processing as dataprocess

import time

"""-------------------------ENERGY USE-------------------------"""


def energy_use_all_households():
    return (
        dcc.Graph(
            id="energy-use-all-chart",
            figure=go.Figure()
        )
    )


def energy_use_one_household():
    return (
        dcc.Graph(
            id="energy-use-one-chart",
            figure=go.Figure(
                data=[
                    go.Pie(
                        values=[0, 0],
                        labels=["Grid", "PV"],
                        marker=dict(colors=['#008000', '#FF0000'])
                    )
                ]
            )
        )
    )


""""-------------------------CONTRACT OVERVIEW-------------------------"""


def contract_all_households():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                'Contract ID', 'Contract start time', 'Contract agreement time', 'Energy used (Wh)', 'Consumer ID',
                'Producer ID'],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="contract-table-all"
        )
    )


def contract_one_household():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                'Contract ID', 'Contract start time', 'Contract agreement time', 'Energy used (Wh)', 'Consumer ID',
                'Producer ID'],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="contract-table-one"
        )
    )


"""-------------------------AVAILABLE VS USED ENERGY-------------------------"""


def energy_consumption_one_run():
    return (
        dcc.Graph(
            id="energy-consumption-graph",
            figure=go.Figure()
        )
    )


def energy_consumption_all_runs():
    return (
        dcc.Graph(
            id="energy-consumption-graph-all-runs",
            figure=go.Figure()
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
    html.Div(html.H3("Simulation to display")),
    html.Span("Choose simulation "),
    dcc.Dropdown(
        id="simulation_choice",
        options=get_dropdown_options(),
        value=get_dropdown_options()[0]["value"]
    ),
    html.Button('Update results', className='btn', id='btn-update'),
    html.Div(id='sim_id', children=[
        html.Br(),
        html.Span("Choose run"),
        html.Div(
            dcc.Dropdown(
                id="run_choice",
                options=[]
            )
        ),
    ]),
    html.Br(),
    html.Div(id='household_id', style={'display': 'none'}, children=[
        html.Span("Choose household"),
        html.Div(
            dcc.Dropdown(
                id="household_choice",
                options=[]
            )
        ),
    ]), html.Br(),
    html.Div(id="graph-content", children=[
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(id='tab_all_households', label='All households', children=[
                html.Br(),
                html.Div(
                    html.H2("Energy used distribution", className="header")
                ),
                html.Div(id="self-consumption-all", className="paragraph"),
                html.Div([
                    energy_use_all_households()
                ], className="pie-chart"),
                html.Br(),

                html.Div(
                    html.H2("Contracts", className="header")
                ),
                html.Div([
                    contract_all_households()
                ], className="contract-table-all"),
                html.Br(),

                html.Div(
                    html.H2("Production and consumption profiles", className="header")
                ),
                html.Div(id='peak-average-ratio-all', className="paragraph"),
                html.Div([
                    energy_consumption_one_run()
                ], className="consumption-graph"),
                html.Br(),
            ]),
            dcc.Tab(id='tab_one_household', label='One household', children=[
                html.Br(),
                html.Div(
                    html.H2("Energy used distribution", className="header")
                ),
                html.Div(id="self-consumption-one", className="paragraph"),
                html.Div([
                    energy_use_one_household()
                ], className="pie-chart"),
                html.Br(),

                html.Div(
                    html.H2("Contracts", className="header")
                ),
                html.Div([
                    contract_one_household()
                ]),
                html.Br(),
                html.Div(
                    html.H3("Peak to average ratio", className="header")
                ),
                html.Div(id='peak-average-ratio-one', className="paragraph"),
                html.Br(),
            ]),
            dcc.Tab(id='tab_all_runs', label='All runs', children=[
                html.Div(
                    html.H2("Production and consumption profiles", className="header")
                ),
                html.Div(id='peak-average-ratio-sum'),
                html.Div(
                    energy_consumption_all_runs()
                )
            ])
        ])
    ], style={"display": "none"})
])

"""-------------------------DROPDOWNS-------------------------"""


@app.callback(Output("simulation_choice", "options"),
              [Input("btn-update", "n_clicks")])
def update_dropdown(n_clicks):
    print("click")
    return get_dropdown_options()


@app.callback(Output("run_choice", "options"),
              [Input("simulation_choice", "value")])
def update_simid_dropdown(value):
    search = re.search(r'_(\d+?)\.', value)
    num = search.group(0)[1:-1]
    sim_options = []
    for val in range(0, int(num)):
        sim_options.append({'label': 'Run {}'.format(val + 1), 'value': '{}'.format(val + 1)})
    return sim_options


@app.callback(Output("graph-content", "style"),
              [Input("run_choice", "value")])
def check_valid_run(run):
    if run is None:
        return {"display": "none"}
    return {"display": "block"}


@app.callback(Output("household_choice", "options"),
              [Input("run_choice", "value")],
              [State("simulation_choice", "value")])
def update_houseid_dropdown(run_choice, simulation_choice):
    contracts = dataprocess.get_contracts(str(simulation_choice))
    contracts = contracts[int(run_choice) - 1]
    house_options = []
    house_id = []
    for contract in contracts:
        before = contract['job_id'].index('[') + 1
        after = contract['job_id'].index(']')
        household_id = contract['job_id'][before:after]
        if household_id not in house_id:
            house_id.append(household_id)
            house_options.append({'label': 'Consumer ID: {}'.format(household_id), 'value': '{}'.format(household_id)})
    return house_options


"""-------------------------CONTRACTS-------------------------"""


# All households
@app.callback(Output("contract-table-all", "rows"),
              [Input("run_choice", "value")],
              [State("simulation_choice", "value")])
def update_contracts(run_choice, simulation_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    rows = []
    for contract in contracts:
        contract["load_profile"] = round(contract["load_profile"].values[-1], 2)
        contract = dataprocess.rename_columns(contract)
        rows.append(contract)
    return rows


# One household
@app.callback(Output("contract-table-one", "rows"),
              [Input("household_choice", "value")],
              [State("run_choice", "value"),
               State("simulation_choice", "value")])
def update_contracts(household_choice, run_choice, simulation_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    rows = []
    for contract in contracts:
        contract["load_profile"] = round(contract.get("load_profile").values[-1], 2)
        contract = dataprocess.rename_columns(contract)
        if contract.get("Consumer ID").startswith('[{}]'.format(household_choice)):
            rows.append(contract)
    return rows


"""-------------------------PIE CHARTS-------------------------"""


# All households
@app.callback(
    Output("energy-use-all-chart", "figure"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def update_pie_chart(run_choice, simulation_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    # print('Contracts used in pie chart: {}'.format(contracts))
    grid = 0
    pv = 0
    for contract in contracts:
        if contract["producer_id"] == 'grid':
            grid += contract["load_profile"].values[-1]
        else:
            pv += contract["load_profile"].values[-1]
    return go.Figure(
        data=[
            go.Pie(
                values=[grid, pv],
                labels=["Grid", "PV"],
                marker=dict(colors=['#FF0000', '#008000'])
            )
        ]
    )


# One household
@app.callback(
    Output("energy-use-one-chart", "figure"),
    [Input("household_choice", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_pie_chart_single_house(household_choice, simulation_choice, run_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    # print('Contracts used in pie chart: {}'.format(contracts))
    grid = 0
    pv = 0
    for contract in contracts:
        if contract["job_id"].startswith('[{}]'.format(household_choice)):
            if contract["producer_id"] == 'grid':
                grid += contract["load_profile"].values[-1]
            else:
                pv += contract["load_profile"].values[-1]
    return go.Figure(
        data=[
            go.Pie(
                values=[grid, pv],
                labels=["Grid", "PV"],
                marker=dict(colors=['#FF0000', '#008000'])
            )
        ]
    )


"""-------------------------SELF CONSUMPTION-------------------------"""


# All households
@app.callback(
    Output("self-consumption-all", "children"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def self_consumption_all(run_choice, simulation_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract.get("producer_id") == 'grid':
            grid += contract.get("load_profile").values[-1]
        else:
            pv += contract.get("load_profile").values[-1]
    return html.P('Total consumption for whole neighbourhood: {}'.format(round(grid + pv, 2)))


# One household
@app.callback(
    Output("self-consumption-one", "children"),
    [Input("household_choice", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_pie_chart_header(household_choice, simulation_choice, run_choice):
    contracts = dataprocess.open_file(simulation_choice)[0]
    contracts = contracts[int(run_choice) - 1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract.get("job_id").startswith('[{}]'.format(household_choice)):
            if contract.get("producer_id") == 'grid':
                grid += contract.get("load_profile").values[-1]
            else:
                pv += contract.get("load_profile").values[-1]
    return html.P('Total consumption for household: {}'.format(round(grid + pv, 2)))


"""-----------------PRODUCTION, CONSUMPTION PROFILES-----------------"""


# All households
@app.callback(
    Output("energy-consumption-graph", "figure"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def update_consumption(run_choice, simulation_choice):
    start_time = time.time()
    print('Run choice: {}'.format(run_choice))
    print('Simulation choice: {}'.format(simulation_choice))
    contracts, profiles = dataprocess.open_file(simulation_choice)
    contracts, profiles = contracts[int(run_choice) - 1], profiles[int(run_choice) - 1]
    # households = dataprocess.neigbourhood_to_household(contracts, profiles)
    profiles = dataprocess.neighbourhood_execution_energy_over_time(contracts, profiles)
    # TODO: Profiles_combined = average
    end_time = time.time()
    print("Time elapsed: " + str(end_time - start_time))
    return go.Figure(
        data=[
            go.Scatter(
                x=profiles[0],
                y=profiles[1],
                name="Energy consumed locally",
                marker=dict(color='#00A6FC')
            ),

            go.Scatter(
                x=profiles[2],
                y=profiles[3],
                name="Energy consumed remotely",
                marker=dict(color='#FF0000')
            ),

            go.Scatter(
                x=profiles[4],
                y=profiles[5],
                name="Energy produced",
                marker=dict(color='#008000')
            ),
        ],
        layout=go.Layout(
            xaxis={
                'title': 'Time [Minutes]'
            },
            yaxis={
                'title': 'Energy [Wh]'
            }
        )
    )


# All runs
@app.callback(
    Output("energy-consumption-graph-all-runs", "figure"),
    [Input("simulation_choice", "value")])
def update_consumption(simulation_choice):
    contracts, profiles = dataprocess.open_file(simulation_choice)
    profiles_combined = dataprocess.neighbourhood_execution_energy_over_time_average(contracts, profiles)
    return go.Figure(
        data=[
            go.Scatter(
                x=profiles_combined[0],
                y=profiles_combined[1],
                name="Energy consumed locally",
                marker=dict(color='#00A6FC')
            ),

            go.Scatter(
                x=profiles_combined[2],
                y=profiles_combined[3],
                name="Energy consumed remotely",
                marker=dict(color='#FF0000')
            ),

            go.Scatter(
                x=profiles_combined[4],
                y=profiles_combined[5],
                name="Energy produced",
                marker=dict(color='#008000')
            ),
        ],
        layout=go.Layout(
            xaxis={
                'title': 'Time [Minutes]'
            },
            yaxis={
                'title': 'Energy [Wh]'
            }
        )
    )


"""-------------------------PEAK TO AV. RATIO-------------------------"""


# All households
@app.callback(
    Output('peak-average-ratio-all', 'children'),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def update_peak_av_ratio(run_choice, simulation_choice):
    contracts, profiles = dataprocess.open_file(simulation_choice)
    out, out_comb = dataprocess.neighbourhood_execution_peak_to_average(contracts, profiles)
    return html.P('Peak to average ratio: {}'.format(round(out[int(run_choice) - 1], 2)))


# One household
@app.callback(
    Output('peak-average-ratio-one', 'children'),
    [Input("household_choice", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_peak_av_ratio(household_choice, simulation_choice, run_choice):
    contracts, profiles = dataprocess.open_file(simulation_choice)
    households = dataprocess.neighbourhood_to_household(contracts, profiles)
    out_data, out_house = dataprocess.household_execution_peak_to_average_ratio(contracts, profiles, households)
    peak_av_ratio = 0
    for i in range(0, len(out_house[int(run_choice) - 1])):
        if out_house[int(run_choice) - 1][i] == household_choice:
            peak_av_ratio += out_data[int(run_choice) - 1][i]
    return html.P('Peak to average ratio: {}'.format(round(peak_av_ratio, 2)))


"""-------------------------DISPLAY'S IN TABS-------------------------"""


@app.callback(
    Output('sim_id', 'style'),
    [Input('tabs', 'value')]
)
def display_none(value):
    if value == 'tab-3':
        return {'display': 'none'}


@app.callback(
    Output('household_id', 'style'),
    [Input('tabs', 'value')]
)
def display_none(value):
    style = ''
    if value == 'tab-2':
        style = {'display': 'block'}
    if (value == 'tab-1') or (value == 'tab-3'):
        style = {'display': 'none'}
    return style
