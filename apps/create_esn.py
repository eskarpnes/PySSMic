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
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.neighbourhood import Neighbourhood
from backend.house import House
from backend.device import Device
from backend.user import User
from app import app

# Returns a list of divs.
main_neighbourhood = None
active_user = None
# TODO: modal for adding house. modal with input field to set houseID


def create_house_tab(house):
    return(dcc.Tab(label='House Id: ' + str(house.id), value=str(house.id)))


def create_house_tabs(nei):
    houses = []
    for house in nei.houses:
        houses.append(create_house_tab(house))
    return houses


def create_house_view(house):
    content = []
    for user in house.users:
        for device in user.devices:
            content.append(
                html.Div(className="DeviceInHouse", children=[
                    html.Span("userid: " + str(user.id) + "\t\t"),
                    html.Span("DeviceID: " + str(device.id) + "\t\t"),
                    html.Span("DeviceName: " + device.name + "\t\t"),
                    html.Span("DeviceTemplate: " + str(device.id) + "\t\t"),
                    html.Span("DeviceType: " + device.type + "\t\t")
                ])
            )
    return content


def displayHouse(house):
    numOfUsers = 0
    numOfDevices = 0
    for user in house.users:
        numOfUsers += 1
        for device in user.devices:
            numOfDevices += 1

    return html.Div(["House",
                     html.Span(str(house.id)),
                     html.Button("Delete house", id="deleteHouse"),
                     html.Button("Configure", id="btnConfigHouse"),
                     html.Br(),
                     html.Span("Number of users: " + str(numOfUsers)),
                     html.Br(),
                     html.Span("Number of devices: " + str(numOfDevices)),
                     html.Div(children=create_house_view(house)),
                     configHouseModal(house)
                     ])


def addHouseToNeighbourhood(houseId):
    global main_neighbourhood
    # lastId = int(neighbourhood.houses[-1].id)
    house = House(houseId)
    main_neighbourhood.houses.append(house)


def configHouseModal(house):
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # header
                        html.Div(
                            [
                                html.Span(
                                    "Configure House" + str(house.id),
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
                                        # Ex: https://github.com/plotly/dash-salesforce-crm/blob/master/apps/leads.py

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                )
                            ],
                            className="row",
                            style={"padding": "2% 8%"},
                        ),
                        dcc.Dropdown(id='user-dropdown', options=[{'label': user.id, 'value': user.id} for user in house.users]),
                        dcc.Dropdown(id='user-device-dropdown'),
                        # create house button
                        html.Span(
                            "Save",
                            id="save_new_house",
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
        id="house_modal",
        style={"display": "none"},
    )


layout = html.Div([
    # hidden div to save data in
    html.Div(id="hidden-div-n-houses", style={'display': 'none'}),
    html.H4("Create a new neighbourhood"),
    html.Div(id="initChoices", children=[
        html.Button("Create from XML", id="btnXmlInput"),
        html.Button("Create a new", id="btnNewNeighbourhood"),
        dcc.Upload(
            id="upload-data",
            children=html.Div([
                'Add neighbourhood XML file by Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '500px',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'none'
            }
        ),
        html.Div(id="newNeighbourhoodInput", children=[
            dcc.Input(id="newNeighbourhoodId", value=0, type="number", style={
                'width': '50pxx'
            }),
            html.Button("Create Neighbourhood", id="btnCreateNewNeighbourhood")
        ],
            style={'display': 'block'}),
    ]),
    html.Div(id="newHouseInput", children=[
        dcc.Input(id="new_house_id", type='number', style={
                'width': '100'}),
        html.Button("Add house", id="btnAddHouse"),
    ]),
    html.Div(id="neighbourhood-info"),
    html.Div(id="tabs"),
])

# takes in a xmlfile and returns a XML Elementree of the neighborhood.


def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'xml' in content_type:
            decoded = base64.b64decode(content_string)
            root = ET.fromstring(decoded)
            return root


def create_neighborhood_object(treeroot):
    nabolag = Neighbourhood(int(treeroot.get("id")))
    for house in treeroot:
        h = House(int(house.get("id")))
        for user in house:
            u = User(int(user.get("id")))
            for device in user:
                d = Device(int(device.find("id").text), device.find("name").text, int(
                    device.find("template").text), device.find("type").text)
                u.devices.append(d)
            h.users.append(u)
        nabolag.houses.append(h)
    return nabolag


"""
Callback function to toggle the xml input field
"""


@app.callback(Output("upload-data", "style"), [Input("btnXmlInput", "n_clicks")])
def showXMLUpload(n):
    if n % 2 == 0:
        return {"display": "none"}
    return {"display": "block"}


"""
Callback to render id inputfield for a new Neighbourhood
"""


@app.callback(Output('newNeighbourhoodInput', 'style'),
              [Input("btnNewNeighbourhood", "n_clicks")])
def showNewNeighbourhoodInput(n):
    if n == 1:
        return {'display': 'block'}
    return {"display": "none"}


# Saves neighbourhood in hidden div on main page, so the output div can update on multiple other events


@app.callback(Output('neibourhood_div', 'children'),
              [Input('upload-data', 'contents'),
               Input('btnCreateNewNeighbourhood', 'n_clicks')],
              [State('newNeighbourhoodInput', 'value')])
def create_house(contents, n, value):
    global main_neighbourhood
    if n and n > 0:
        main_neighbourhood = Neighbourhood(value)
    else:
        root = parse_contents(contents)
        main_neighbourhood = create_neighborhood_object(root)
    nabolag = main_neighbourhood.to_json()
    return html.Div(nabolag)


@app.callback(Output('tabs', 'children'),
              [Input('neibourhood_div', 'children'),
               Input('btnAddHouse', 'n_clicks')],
              [State('new_house_id', 'value')])
def showNeihbourhood(dictionary, n, value):
    global main_neighbourhood
    global active_house
    if n and n > 0:
        main_neighbourhood.houses.append(House(value))
        n = 0
    tabs = create_house_tabs(main_neighbourhood)
    return html.Div(children=[
        dcc.Tabs(id='neighbourhoodTabs', children=tabs),
        html.Div(id='tabs-content', children=["some cool content"])
    ])


@app.callback(Output('initChoices', 'style'), [Input('tabs', 'children')])
def hideButton(children):
    if len(children) > 1:
        return {'display': 'none'}

# generate content for tabs
@app.callback(Output('tabs-content', 'children'),
              [Input('neighbourhoodTabs', 'value')])
def render_content(value):
    global main_neighbourhood
    if value is not None:
        tabId = int(value)
    else:
        # get the id of first house
        tabId = int(main_neighbourhood.houses[0].id)
    if main_neighbourhood is not None:
        house = main_neighbourhood.findHouseById(tabId)
        if house is not None:
            dis = displayHouse(house)
            return html.Div([dis])


@app.callback(Output("house_modal", "style"), [Input("btnConfigHouse", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# reset to 0 add button n_clicks property

@app.callback(
    Output("btnConfigHouse", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"),
     Input("save_new_house", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0

@app.callback(Output("user-device-dropdown", "options"), [Input("user-dropdown", "value")])
def setUserDeviceOptions(value):
    return [{'label': i, 'value': i} for i in [1,2,3]]