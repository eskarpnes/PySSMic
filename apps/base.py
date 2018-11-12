import dash_core_components as dcc
import dash_html_components as html


"""
This represents a base file which follows every layout
"""

header = html.Div([
    html.H1(children="CoSSMic Simulator"),
    html.Div([
        dcc.Link("Home", href="/"),
        dcc.Link("Create Simulation", href="/apps/create_sim"),
        dcc.Link("Create neighbourhood", href="/apps/create_esn"),
        dcc.Link("Results", href="/apps/simulate_esn")
    ], className="links")
], className="header")


footer = html.Div([
    "© Customer Driven Project for SINTEF Digital"
], className="footer")
