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
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Go to Create Simulation', href='/apps/create_sim'),
    html.Br(),
    dcc.Link("Create neighbourhood", href='/apps/create_esn')

], className="header")


footer = html.Div([
    "This is an awesome footer for the PySSMiC simulator"
], className="footer")
