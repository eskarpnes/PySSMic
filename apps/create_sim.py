import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
import os

from app import app
from threaded_simulator import ThreadedSimulator
import pandas as pd


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
                options=get_dropdown_options()
            ),

            html.Div(className="selectDays", children=[
                html.Span("Days to simulate: "),
                dcc.Input(id="days", type="int"),
            ]),

            html.Div(className="selectAlgo", children=[
                html.Span("Select Optimization Algorithm(s): "),
                dcc.Dropdown(
                    id="algo",
                    options=[
                        {'label': '50/50', 'value': '1'},
                        {'label': 'Powell', 'value': '2'},
                    ]
                )
            ]),

            html.Div(className="selectRuns", children=[
                html.Span("Select number of runs: "),
                dcc.Input(id="runs", type="int")
            ]),

            html.A(html.Button('Start simulation',
                               className='btnSimulate', id='btn-simulate'))

        ])
    ])

])


@app.callback(
    Output(component_id="datatableDiv", component_property="children"),
    events=[Event("btn-simulate", "click")],
)
def on_click(neighbourhood, days, algo, runs):
    config = {
        "neighbourhood": neighbourhood,
        "length": days*86400,
        "timefactor": 0.000000001,
        "algo": algo,
        "runs": runs
    }

    print(config)

    def callback(contracts, profiles):
        print(contracts)
        print(profiles)

    #sim = ThreadedSimulator(config, callback)
    #sim.start()
