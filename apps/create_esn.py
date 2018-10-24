import base64
import datetime
import io
import json
import xml.etree.ElementTree as ET
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt


from app import app


def newHousePopup():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # header
                        html.Div(
                            [
                                html.Span(
                                    "New House - ID X",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="leads_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="popup",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),
                        # form
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Here you can add settins for the popup. See link commented in code",
                                        #Ex: https://github.com/plotly/dash-salesforce-crm/blob/master/apps/leads.py

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                            ],
                            className="row",
                            style={"padding": "2% 8%"},
                        ),
                        #create house button
                        html.Span(
                            "Submit",
                            id="submit_new_lead",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="leads_popup",
        style={"display": "none"},
    )


layout = html.Div([
    # hidden div to save data in
    html.Div(id="hidden-div", style={'display': 'none'}),
    html.H2("Create a new neighbourhood"),
    dcc.Link('Go back to Create Simulation', href='/apps/create_sim'),
    html.Br(),
    html.Button("Add house", id='btnAddHouse'),
    html.Br(),
    html.Button("Add user in house"),
    html.Br(),
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
    dt.DataTable(
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id="datatable"
    ),
    html.Div(id='output'),

    newHousePopup()
])

# takes in a xmlfile and returns a XML Elementree of the neighborhood.


def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'xml' in content_type:
            decoded = base64.b64decode(content_string)
            root = ET.fromstring(decoded)
            return root

# Creates a dataFrame of the root


def eltreeToDataframe(treeRoot):
    df = pd.DataFrame(columns=[
        "houseId", "deviceId", "UserId", "DeviceName", "DevTemp", "DevType"])
    for house in treeRoot:
        for user in house:
            for device in user:
                df = df.append({"houseId": (house.get("id")), "deviceId": (device.find("id").text), "UserId": (user.get("id")), "DeviceName": (device.find("name").text), "DevTemp": (device.find("template").text), "DevType": (device.find("type").text)},
                               ignore_index=True)
    #df.set_index("deviceId", inplace=True)
    return df


def addDevice(data, houseId, deviceId, userId, deviceName, devTemp, devType):
    df = data
    df2 = pd.DataFrame([[houseId, userId, deviceName, devTemp, devType]], index=[
        deviceId], columns=["houseId", "UserId", "DeviceName", "DevTemp", "DevType"])
    return pd.concat([df, df2])


def removeDevice(data, deviceId):
    df = data
    df = df.drop(index=deviceId)
    return df


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



"""
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

# hide/show popup
@app.callback(Output("leads_popup", "style"), [Input("btnAddHouse", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}

# reset to 0 add button n_clicks property
@app.callback(
    Output("btnAddHouse", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"), Input("submit_new_lead", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0
