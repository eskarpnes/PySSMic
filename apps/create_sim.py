import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

# TODO: Add/remove users from the neighbourhood
# TODO: Number of days simulated
# TODO: Configure simulated weather
# TODO: Review the use of green energy
# TODO: Specify which optimization algorithm to be used in simulation

layout = html.Div(children=[
    html.Div(className="content", children=[


        html.Div(className="simulatorSetup", children=[
            html.Span("Select ESN:"),
            html.A(html.Button("Create ESN", className="btnAddEsn"),
                   href='/apps/create_esn'),
            dcc.Dropdown(
                options=[
                    {'label': "Flatåsen", "value": "1"},
                    {'label': "Ila", "value": "2"},
                    {'label': "Byåsen", "value": "3"}
                ]
            ),


            html.Div(className="selectDays", children=[
                html.Span("Days to simulate: "),
                html.Span(id="numDays"),
                dcc.Input(id="inputDays", type="int"),
                html.Button("Set", className="btnSet")
            ]),

            html.Div(className="selectAlgo", children=[
                html.Span("Select Optimization Algorithm(s): "),
                dcc.Dropdown(
                    options=[
                        {'label': '50/50', 'value': '1'},
                        {'label': 'Powell', 'value': '2'},
                    ],
                    multi=True,
                )
            ]),

            html.Div(className="selectWeather", children=[
                html.Span("Select type of weather: "),
                dcc.Dropdown(
                    options=[
                        {'label': 'Sunny', 'value': 'SUN'},
                        {'label': 'Cloudy', 'value': 'CLOUD'}
                    ],
                    value='SUN'
                )
            ]),

            html.A(html.Button('Start simulation', className='btnSimulate'),
                   href='/apps/simulate_esn')


        ])
    ])

])


@app.callback(
    Output(component_id="numDays", component_property="children"),
    [Input(component_id="inputDays", component_property="value")],
)
def update_weather(input_weather):
    return input_weather
