import dash_core_components as dcc
import dash_html_components as html
import os.path
from definitions import URL_STYLE

"""
This represents a base file which follows every layout
"""


header = html.Div([
    html.Div(id="logo-img", children=[
        html.Img(src=os.path.join("assets", "logo_pyssmic.png"), style={"transform": "scale(0.5, 0.5)"})
    ]),
    html.Div([
        dcc.Link("Home", href="/", style=URL_STYLE),
        dcc.Link("Create Simulation", href="/apps/create_sim", style=URL_STYLE),
        dcc.Link("Create neighbourhood", href="/apps/create_esn", style=URL_STYLE),
        dcc.Link("Results", href="/apps/simulate_esn", style=URL_STYLE)
    ], className="links")
], className="header")


footer = html.Div([
    "© Customer Driven Project for SINTEF Digital"
], className="footer")
