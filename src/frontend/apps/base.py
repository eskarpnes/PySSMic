import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from app import app

"""
This represents a base file which follows every layout
"""

header = html.Div([
    html.H1(children="CoSSMic Simulator")
], className="header")


footer = html.Div([
    "This is an awesome footer for the PySSMiC simulator"
], className="footer")
