import base64
import datetime
import io
import json
import xml.etree.ElementTree as ET

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


from src.frontend.app import app

layout = html.Div([
    html.H2("Create a new neighbourhood"),
    dcc.Link('Go back to Create Simulation', href='/apps/create_sim'),

    dcc.Upload(
        id="upload-data",
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    html.Div(id='output-data-upload'),

])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    countries = []
    tree = ET.fromstring(decoded)
    nei = create_neighborhood_list(tree)
    return nei

# Takes in a xml.Elementree.Element and produces a neighborhood
# TODO: change the print statements with what you decide to do


def create_neighborhood_list(neighborhood):
    nh = []
    print("---House---")
    for house in neighborhood:
        h = [house.get("id")]
        print(house.get("id"))
        for user in house:
            print(user.get("id"))
            u = [user.get("id")]
            for device in user:
                print(device.find("id").text)
                u.append(device.find("id").text)
            h.append(u)
        nh.append(h)
    print("---new house ---")

    return nh


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
