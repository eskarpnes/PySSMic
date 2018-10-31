import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
import os
import pickle

from app import app
from threaded_simulator import ThreadedSimulator
import time


# TODO: Add/remove users from the neighbourhood
# TODO: Number of days simulated
# TODO: Configure simulated weather
# TODO: Review the use of green energy
# TODO: Specify which optimization algorithm to be used in simulation

def get_dropdown_options():
    options = next(os.walk('input'))[1]
    dropdown = []
    for option in options:
        dropdown.append({
            'label': option,
            'value': option
        })
    return dropdown


layout = html.Div(children=[
    html.Div(className="content", children=[

        html.Div(className="simulatorSetup", children=[
            html.Span("Select ESN:"),
            html.A(html.Button("Create ESN", className="btnAddEsn"),
                   href='/apps/create_esn'),
            dcc.Dropdown(
                id="neighbourhood",
                options=get_dropdown_options(),
                value=get_dropdown_options()[0]["value"]
            ),

            html.Div(className="selectDays", children=[
                html.Span("Days to simulate: "),
                dcc.Input(id="days", type="int", value=1),
            ]),

            html.Div(className="selectAlgo", children=[
                html.Span("Select Optimization Algorithm(s): "),
                dcc.Dropdown(
                    id="algo",
                    options=[
                        {'label': '50/50', 'value': '50/50'},
                        {'label': 'Basinhopping', 'value': 'basinhopping'},
                    ],
                    value="powell"
                )
            ]),

            html.Div(className="selectRuns", children=[
                html.Span("Select number of runs: "),
                dcc.Input(id="runs", type="int", value="1")
            ]),

            html.A(html.Button('Start simulation',
                               className='btnSimulate', id='btn-simulate'))
        ])
    ])

])


@app.callback(
    Output(component_id="datatableDiv", component_property="children"),
    [Input("btn-simulate", "n_clicks")],
    [State("neighbourhood", "value"),
     State("days", "value"),
     State("algo", "value"),
     State("runs", "value")]
)
def on_click(n_clicks, neighbourhood, days, algo, runs):
    config = {
        "neighbourhood": neighbourhood,
        "length": int(days) * 86400,
        "timefactor": 0.00001,
        "algo": algo,
        "runs": int(runs)
    }
    print(config)
    now_string = time.strftime("%d%b%y-%H%M")
    print(now_string)
    filename = now_string + "_" + neighbourhood + "_" + algo.replace("/", "") + "_" + str(runs)

    def save_results(contracts, profiles):
        print("Saving results")
        pathname = os.path.join("results", filename)
        with open(pathname + ".pkl", "wb") as f:
            pickle.dump((contracts, profiles), f)

    sim = ThreadedSimulator(config, save_results)
    sim.start()
    return 0
