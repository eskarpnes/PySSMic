import dash_core_components as dcc
import dash_html_components as html
import os.path
from definitions import URL_STYLE

"""
This represents a base file which follows every layout
"""


header = html.Div([
    html.Div(id="logo-img", children=[
        html.Img(src=os.path.join("assets", "logo_pyssmic.png"))
    ]),
    html.Div([
        dcc.Link("Home", href="/", style=URL_STYLE),
        dcc.Link("Create Simulation", href="/apps/create_sim", style=URL_STYLE),
        dcc.Link("Create neighbourhood", href="/apps/create_esn", style=URL_STYLE),
        dcc.Link("Results", href="/apps/results", style=URL_STYLE)
    ], className="links")
], className="header")
