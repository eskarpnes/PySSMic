import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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
            html.Div(className="selectHorizontal", children=[
                dcc.Dropdown(
                    id="neighbourhood",
                    options=get_dropdown_options(),
                    value=get_dropdown_options()[0]["value"]
                ),
                html.Div(className="btnContainer", children=[
                    html.A(html.Button("Create ESN", className="btnAddEsn"),
                           href='/apps/create_esn')
                ])
            ]),

            html.Div(className="selectVertical", children=[
                html.Div(className="inputText", children=[
                    html.Span("Days to simulate: ")
                ]),
                dcc.Input(id="days", type="int", value=1),
            ]),

            html.Div(className="selectHorizontal", children=[
                html.Div(className="selectVertical", children=[
                    html.Span("Select Optimization Algorithm(s): "),
                    dcc.Dropdown(
                        id="algo",
                        options=[
                            {'label': '50/50', 'value': 'fifty_fifty'},
                            {'label': 'L-BFGS-B', 'value': 'L_BFGS_B'},
                            {'label': 'SLSQP', 'value': 'SLSQP'},
                            {'label': 'TNC', 'value': 'TNC'},
                        ],
                    )
                ]),

                html.Div(className="selectVertical", children=[
                    html.Div(className="inputText", children=[
                        html.Span("Step size")
                    ]),
                    dcc.Input(id="eps", type="float", value=0.0001),
                ]),

                html.Div(className="selectVertical", children=[
                    html.Div(className="inputText", children=[
                        html.Span("Tolerance")
                    ]),
                    dcc.Input(id="tol", type="float", value=1000.0),
                ]),
            ]),


            html.Div(className="selectVertical", children=[
                html.Div(className="inputText", children=[
                    html.Span("Number of runs: ")
                ]),
                dcc.Input(id="runs", type="int", value="1")
            ]),

            html.Div(className="startContainer", children=[
                html.A(html.Button('Start simulation',
                                   className='btnSimulate', id='btn-simulate')),
                html.Div(id="simulatorRunning", style={"display": "none"})
            ])
        ])
    ])

])


@app.callback(
    Output(component_id='btn-simulate', component_property='disabled'),
    [Input('neighbourhood', 'value'),
     Input('days', 'value'),
     Input('algo', 'value'),
     Input('eps', 'value'),
     Input('tol', 'value'),
     Input('runs', 'value')]
)
def check_button_disable(neighbourhood, days, algo, eps, tol, runs):
    if days in ["", "0"]:
        days = None
    if runs in ["", "0"]:
        runs = None
    if None in [neighbourhood, days, algo, eps, tol, runs]:
        return True
    else:
        return False


@app.callback(
    Output(component_id="simulatorRunning", component_property="children"),
    [Input("btn-simulate", "n_clicks")],
    [State("neighbourhood", "value"),
     State("days", "value"),
     State("algo", "value"),
     State("eps", "value"),
     State("tol", "value"),
     State("runs", "value")]
)
def on_click(n_clicks, neighbourhood, days, algo, eps, tol, runs):
    config = {
        "neighbourhood": neighbourhood,
        "length": int(days) * 86400,
        "timefactor": 0.00001,
        "algo": algo,
        "eps": eps,
        "tol": tol,
        "runs": int(runs)
    }
    print(config)
    now_string = time.strftime("%d%b%y_%H%M")
    print(now_string)
    filename = now_string + "_" + neighbourhood + "_" + algo.replace("/", "") + "_" + str(runs)

    sim = ThreadedSimulator(config)

    # Here you can start a loading screen if you want
    contracts, profiles = sim.start()
    # And here you must stop it!

    print("Saving results")
    pathname = os.path.join("results", filename)
    with open(pathname + ".pkl", "wb") as f:
        pickle.dump((contracts, profiles), f)
    return 0
