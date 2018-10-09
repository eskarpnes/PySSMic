import base64
import datetime
import io
import json
import xml.etree.ElementTree as ET

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


from app import app


layout = html.Div([
    # hidden div to save data in
    html.Div(id="hidden-div", style={'display': 'none'}),
    html.H2("Create a new neighbourhood"),
    dcc.Link('Go back to Create Simulation', href='/apps/create_sim'),
    html.Div([dcc.Input(id="house_id", value='House ID', type='text'),
              html.Button("Add house", id='btnAddHouse')]),

    html.Button("Add user in house"),
    html.Button("Add a userdevice"),

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
        }
    ),
    html.Div(id='output')
])

# takes in a xmlfile and returns a XML Elementree of the neighborhood.


def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'xml' in content_type:
            decoded = base64.b64decode(content_string)
            root = ET.fromstring(decoded)
            return root


# Creates a simple html output for the neighborhood input (XML file)


def create_neighborhood_html(neighborhood):
    htmlString = "<div>"
    htmlString += "Nabolag:"

    houses = []
    for house in neighborhood:
        htmlString += "<div>"
        htmlString += "Hus id: " + str(house.get("id"))
        houses.append(house)
        for user in house:
            htmlString += "<div>"
            htmlString += "user id: " + str(user.get("id")) + "<ul>"
            for device in user:
                htmlString += "<li> device id: " + \
                    str(device.find("id").text) + \
                    " Name: " + str(device.find("name").text) + \
                    " Template: " + str(device.find("template").text) + \
                    " Type: " + str(device.find("type").text) + \
                    "</li>"  # closes device listelement
            htmlString += "</ul> </div> <br />"  # closes list and user element
        htmlString += "</div>  <br />"  # closes house div
    htmlString += "</div>"  # closes neighborhood
    print(houses)
    return htmlString


@app.callback(Output('output', 'children'),
              [Input('upload-data', 'contents')])
def update_output(contents):
    root = parse_contents(contents)
    htmlstr = create_neighborhood_html(root)
    return html.Div([
        html.Iframe(
            sandbox='',
            height=500,
            width=600,
            srcDoc=htmlstr
        )
    ])


"""
@app.callback(Output('hidden-div', 'children'),
              [Input('upload-data', 'contents')])
def update_output(contents):
    root = parse_contents(contents)
    htmlstr = create_neighborhood_html(root)
    root_string = ET.tostring(root, 'utf-8', method="xml")
    return html.Div([
        type(root_string)
    ])



@app.callback(Output('output', 'children'),
              [Input('btnAddHouse', 'contents')])
def update_neigborhood(neighborhood):
    htmlstr = create_neighborhood_html(neighborhood)
    return html.Div([
        html.Iframe(
            sandbox='',
            height=500,
            width=600,
            srcDoc=htmlstr
        )
    ])
"""
