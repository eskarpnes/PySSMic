import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
import plotly.graph_objs as go
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
                        marker=dict(colors=["#008000", "#FF0000"])
                    )
                ]
            )
        )
    )


def energy_use_deviation():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                "Run ID", "PV consumption (Wh)", "Grid consumption (Wh)", "Total consumption (Wh)"],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="energy-use-deviation"
        )
    )


""""-------------------------CONTRACT OVERVIEW-------------------------"""


def contract_all_households():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                "Contract ID", "Contract start time", "Contract agreement time", "Energy used (Wh)", "Consumer ID",
                "Producer ID"],
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
                "Contract ID", "Contract start time", "Contract agreement time", "Energy used (Wh)", "Consumer ID",
                "Producer ID"],
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
            id="energy-consumption-graph-one-run",
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


def get_simulation_options():
    print("Loading options")
    options = []
    for root, dirnames, filenames in os.walk("results"):
        for filename in filenames:
            if filename.endswith(".pkl"):
                options.append({
                    "label": filename[:-4], "value": filename}
                )
    if not options:
        options.append({"label": "No results saved.", "value": []})
    return options


"""-------------------------LAYOUT-------------------------"""

layout = html.Div(children=[
    # Shared layout for all tabs
    html.Div(html.H3("Simulation to display")),
    html.Span("Choose simulation"),
    dcc.Dropdown(
        id="simulation_choice",
        options=get_simulation_options(),
        value=get_simulation_options()[0]["value"]
    ),
    html.Button("Update results", className="btn", id="btn-update"),
    html.Div(id="run_id", children=[
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
    html.Div(id="household_id", style={"display": "none"}, children=[
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
            # Tab 1: One run - All households
            dcc.Tab(id="tab_all_households", label="All households", children=[
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

                html.Div(children=[
                    html.H3("Peak to average value for all houses", className="header"),
                    dcc.Input(id="par-interval-all", type="int", placeholder="Insert interval in minutes"),
                    html.Div(id="peak-average-ratio-all-consumer"),
                    html.Div(id="peak-average-ratio-all-producer")
                ], className="selectVertical"),
                html.Div([
                    html.H2("Production and consumption profiles", className="header"),
                    energy_consumption_one_run()
                ], className="consumption-graph"),
                html.Br(),
            ]),
            # Tab 2: One run - One household
            dcc.Tab(id="tab_one_household", label="One household", children=[
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
                html.Div(children=[
                    html.H3("Peak to average value for one house", className="header"),
                    dcc.Input(id="par-interval-one", type="int", placeholder="Insert interval in minutes"),
                    html.Div(id="peak-average-ratio-one-consumer"),
                    html.Div(id="peak-average-ratio-one-producer")
                ], className="selectVertical"),
                html.Br(),
            ]),
            # Tab 3: All runs - All households
            dcc.Tab(id="tab_all_runs", label="All runs", children=[
                html.Div(children=[
                    html.H2("Deviation of energy use"),
                    html.Div(id="standard-deviation")
                ]),
                html.Div(
                    energy_use_deviation()
                ),
                html.Div(
                    html.H2("Average production and consumption profiles", className="header")
                ),
                html.Div(id="peak-average-ratio-sum"),
                html.Div(
                    energy_consumption_all_runs()
                )
            ])
        ])
    ], style={"display": "none"})
])

"""-------------------------DROPDOWNS-------------------------"""


# Simulation dropdown
@app.callback(Output("simulation_choice", "options"),
              [Input("btn-update", "n_clicks")])
def update_simulation_dropdown(n_clicks):
    print("click")
    return get_simulation_options()


# Run dropdown
@app.callback(Output("run_choice", "options"),
              [Input("simulation_choice", "value")])
def update_runid_dropdown(simulation):
    search = re.search(r"_(\d+?)\.", simulation)
    num = search.group(0)[1:-1]
    sim_options = []
    for i in range(int(num)):
        sim_options.append({"label": "Run {}".format(i + 1), "value": "{}".format(i + 1)})
    return sim_options


@app.callback(Output("run_choice", "value"),
              [Input("simulation_choice", "value")]
              )
def set_result_to_none(simulation):
    return None


# Household dropdown
@app.callback(Output("graph-content", "style"),
              [Input("simulation_choice", "value"),
               Input("run_choice", "value"),
               Input("household_choice", "value"),
               Input("tabs", "value")]
              )
def check_valid_run(simulation, run, house, tab):
    if run is None and tab != "tab-3":
        return {"display": "none"}
    if tab == "tab-2":
        if house is None:
            return {"display": "none"}
    if tab == "tab-3":
        if simulation is None:
            return {"display": "none"}
    return {"display": "block"}


@app.callback(Output("household_choice", "options"),
              [Input("run_choice", "value")],
              [State("simulation_choice", "value")])
def update_houseid_dropdown(run, simulation):
    contracts = dataprocess.get_contracts(str(simulation))
    contracts = contracts[int(run) - 1]
    house_options = []
    house_id = []
    for contract in contracts:
        before = contract["job_id"].index("[") + 1
        after = contract["job_id"].index("]")
        household_id = contract["job_id"][before:after]
        if household_id not in house_id:
            house_id.append(household_id)
            house_options.append({"label": "Consumer ID: {}".format(household_id), "value": "{}".format(household_id)})
    return house_options


"""-------------------------CONTRACTS-------------------------"""


# All households
@app.callback(Output("contract-table-all", "rows"),
              [Input("run_choice", "value")],
              [State("simulation_choice", "value")])
def update_contracts(run, simulation):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run)-1]
    rows = []
    for contract in contracts:
        contract["load_profile"] = round(contract["load_profile"].values[-1], 2)
        contract["time"] = dataprocess.convert(contract["time"])
        contract["time_of_agreement"] = dataprocess.convert(contract["time_of_agreement"])
        contract = dataprocess.rename_columns(contract)
        rows.append(contract)
    return rows


# One household
@app.callback(Output("contract-table-one", "rows"),
              [Input("household_choice", "value")],
              [State("run_choice", "value"),
               State("simulation_choice", "value")])
def update_contracts(household, run, simulation):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run)-1]
    rows = []
    for contract in contracts:
        if contract.get("job_id").startswith("[{}]".format(household)):
            contract["load_profile"] = round(contract.get("load_profile").values[-1], 2)
            contract["time"] = dataprocess.convert(contract["time"])
            contract["time_of_agreement"] = dataprocess.convert(contract["time_of_agreement"])
            contract = dataprocess.rename_columns(contract)
            rows.append(contract)
    return rows


"""-------------------------PIE CHARTS-------------------------"""


# All households
@app.callback(
    Output("energy-use-all-chart", "figure"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def update_pie_chart(run, simulation):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run)-1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract["producer_id"] == "grid":
            grid += contract["load_profile"].values[-1]
        else:
            pv += contract["load_profile"].values[-1]
    return go.Figure(
        data=[
            go.Pie(
                values=[grid, pv],
                labels=["Grid", "PV"],
                marker=dict(colors=["#DF6461", "#2ecc71"])
            )
        ]
    )


# One household
@app.callback(
    Output("energy-use-one-chart", "figure"),
    [Input("household_choice", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_pie_chart_single_house(household, simulation, run):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run)-1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract["job_id"].startswith("[{}]".format(household)):
            if contract["producer_id"] == "grid":
                grid += contract["load_profile"].values[-1]
            else:
                pv += contract["load_profile"].values[-1]
    return go.Figure(
        data=[
            go.Pie(
                values=[grid, pv],
                labels=["Grid", "PV"],
                marker=dict(colors=["#DF6461", "#2ecc71"])
            )
        ]
    )


"""-------------------------SELF CONSUMPTION-------------------------"""


# All households
@app.callback(
    Output("self-consumption-all", "children"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def self_consumption_all(run, simulation):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run) - 1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract.get("producer_id") == "grid":
            grid += contract.get("load_profile").values[-1]
        else:
            pv += contract.get("load_profile").values[-1]
    return html.P("Total consumption for whole neighbourhood: {}".format(round(grid+pv, 2)))


# One household
@app.callback(
    Output("self-consumption-one", "children"),
    [Input("household_choice", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_pie_chart_header(household, simulation, run):
    contracts = dataprocess.open_file(simulation)[0]
    contracts = contracts[int(run)-1]
    grid = 0
    pv = 0
    for contract in contracts:
        if contract.get("job_id").startswith("[{}]".format(household)):
            if contract.get("producer_id") == "grid":
                grid += contract.get("load_profile").values[-1]
            else:
                pv += contract.get("load_profile").values[-1]
    return html.P("Total consumption for household: {}".format(round(grid+pv, 2)))


"""-----------------PRODUCTION, CONSUMPTION PROFILES-----------------"""


# All households
@app.callback(
    Output("energy-consumption-graph-one-run", "figure"),
    [Input("run_choice", "value")],
    [State("simulation_choice", "value")])
def update_consumption(run, simulation):
    start_time = time.time()
    print("Run choice: {}".format(run))
    print("Simulation choice: {}".format(simulation))
    contracts, profiles = dataprocess.open_file(simulation)
    contracts, profiles = contracts[int(run)-1], profiles[int(run)-1]
    profiles = dataprocess.neighbourhood_execution_energy_over_time(contracts, profiles)
    end_time = time.time()
    print("Time elapsed: {}".format(end_time-start_time))
    return go.Figure(
        data=[
            go.Scatter(
                x=profiles[0],
                y=profiles[1],
                name="Energy consumed locally",
                marker=dict(color="#00A6FC")
            ),

            go.Scatter(
                x=profiles[2],
                y=profiles[3],
                name="Energy consumed remotely",
                marker=dict(color="#FF0000")
            ),

            go.Scatter(
                x=profiles[4],
                y=profiles[5],
                name="Energy produced",
                marker=dict(color="#008000")
            ),
        ],
        layout=go.Layout(
            xaxis={
                "title": "Time [Minutes]"
            },
            yaxis={
                "title": "Energy [W]"
            }
        )
    )


# All runs
@app.callback(
    Output("energy-consumption-graph-all-runs", "figure"),
    [Input("simulation_choice", "value")])
def update_consumption(simulation):
    contracts, profiles = dataprocess.open_file(simulation)
    profiles_combined = dataprocess.neighbourhood_execution_energy_over_time_average(contracts, profiles)
    return go.Figure(
        data=[
            go.Scatter(
                x=profiles_combined[0],
                y=profiles_combined[1],
                name="Energy consumed locally",
                marker=dict(color="#00A6FC")
            ),

            go.Scatter(
                x=profiles_combined[2],
                y=profiles_combined[3],
                name="Energy consumed remotely",
                marker=dict(color="#FF0000")
            ),

            go.Scatter(
                x=profiles_combined[4],
                y=profiles_combined[5],
                name="Energy produced",
                marker=dict(color="#008000")
            ),
        ],
        layout=go.Layout(
            xaxis={
                "title": "Time [Minutes]"
            },
            yaxis={
                "title": "Energy [W]"
            }
        )
    )


"""-------------------------PEAK TO AV. RATIO-------------------------"""


# All households consumed
@app.callback(
    Output("peak-average-ratio-all-consumer", "children"),
    [Input("run_choice", "value"),
     Input("par-interval-all", "value")],
    [State("simulation_choice", "value")])
def update_peak_av_ratio(run, interval, simulation):
    if interval in [None, ""]:
        return html.P("Not a valid interval")
    contracts, profiles = dataprocess.open_file(simulation)
    contracts = contracts[int(run)-1]
    par = dataprocess.peak_to_average_ratio_consumption(contracts, int(interval))
    return html.P("Consumed peak to average ratio: {}".format(round(par, 2)))


@app.callback(
    Output("peak-average-ratio-all-producer", "children"),
    [Input("run_choice", "value"),
     Input("par-interval-all", "value")],
    [State("simulation_choice", "value")])
def update_peak_av_ratio(run, interval, simulation):
    if interval in [None, ""]:
        return html.P("")
    profiles = dataprocess.get_profiles(simulation)
    profiles = profiles[int(run)-1]
    par = dataprocess.peak_to_average_ratio_production(list(profiles.values()), int(interval))
    return html.P("Produced peak to average ratio: {}".format(round(par, 2)))


# One household consumed
@app.callback(
    Output("peak-average-ratio-one-consumer", "children"),
    [Input("household_choice", "value"),
     Input("par-interval-one", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_peak_av_ratio_single_house(household, interval, simulation, run):
    contracts, profiles = dataprocess.open_file(simulation)
    contracts = contracts[int(run)-1]
    contracts_for_house = dataprocess.get_contracts_for_house(household, contracts)
    par = dataprocess.peak_to_average_ratio_consumption(contracts_for_house, int(interval))
    return html.P("Consumed peak to average ratio: {}".format(round(par, 2)))


@app.callback(
    Output("peak-average-ratio-one-producer", "children"),
    [Input("household_choice", "value"),
     Input("par-interval-one", "value")],
    [State("simulation_choice", "value"),
     State("run_choice", "value")])
def update_peak_av_ratio_single_house_producer(household, interval, simulation, run):
    if interval in [None, ""]:
        return html.P("")
    profiles = dataprocess.get_profiles(simulation)
    profiles = profiles[int(run)-1]
    profiles_for_house = dataprocess.get_profiles_for_house(household, profiles)
    par = dataprocess.peak_to_average_ratio_production(profiles_for_house, int(interval))
    return html.P("Produced peak to average ratio: {}".format(round(par, 2)))


"""-------------------------DEVIATION-------------------------"""


@app.callback(
    Output("energy-use-deviation", "rows"),
    [Input("simulation_choice", "value")]
)
def energy_use_deviation(simulation):
    search = re.search(r"_(\d+?)\.", simulation)
    runs = search.group(0)[1:-1]
    record_list = []
    for i in range(int(runs)):
        energy_use = dataprocess.get_energy_use(i, simulation)
        record_list.append({"Run ID": "{}".format(i+1), "PV consumption (Wh)": "{}".format(energy_use[0]), "Grid consumption (Wh)": "{}".format(energy_use[1]), "Total consumption (Wh)": "{}".format(energy_use[2])})
    return record_list


@app.callback(
    Output("standard-deviation", "children"),
    [Input("simulation_choice", "value")]
)
def standard_deviation(simulation):
    results = dataprocess.get_standard_deviation(simulation)
    std = results[0]
    mean = results[1]
    return html.P("Mean local consumption: {} Wh. Standard deviation: {}".format(mean, std))


"""-------------------------DISPLAY"S IN TABS-------------------------"""


@app.callback(
    Output("run_id", "style"),
    [Input("tabs", "value")]
)
def display_none(value):
    if value == "tab-3":
        return {"display": "none"}


@app.callback(
    Output("household_id", "style"),
    [Input("tabs", "value")]
)
def display_none(value):
    style = ""
    if value == "tab-2":
        style = {"display": "block"}
    if (value == "tab-1") or (value == "tab-3"):
        style = {"display": "none"}
    return style
