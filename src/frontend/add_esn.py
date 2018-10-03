import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

add_esn = dash.Dash(__name__)

add_esn.layout = html.Div(children=[
    html.H2("Create a new neighbourhood")

    html.Div(className="esnInput", children=[

    ])
])


if __name__ == '__main__':
    add_esn.run_server(debug=True)
