import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from app import app

"""
This represents a base file which follows every layout
"""

header = html.Div([
    html.H1(children="CoSSMic Simulator"),
    html.Div([
        dcc.Link('Home', href='/'),
        dcc.Link('Go to Create Simulation', href='/apps/create_sim'),
        dcc.Link("Create neighbourhood", href='/apps/create_esn'),
        dcc.Link('Simulation', href='/apps/simulate_esn')
    ], className="links")
], className="header")


footer = html.Div([
    "This is an awesome footer for the PySSMiC simulator"
], className="footer")
