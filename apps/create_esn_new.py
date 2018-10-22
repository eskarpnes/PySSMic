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
active_house = None
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
                    html.Span(str(device.id)),
                    html.Span(device.name),
                    html.Span(str(device.id)),
                    html.Span(device.type)
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
                     html.Br(),
                     html.Span("Number of users: " + str(numOfUsers)),
                     html.Button("Add user", id="addUserInHouse"),
                     html.Br(),
                     html.Span("Number of devices: " + str(numOfDevices)),
                     html.Button("Add device", id="addUserDeviceInHouse"),
                     html.Div(children=create_house_view(house))
                     ])


def addHouseToNeighbourhood(houseId):
    global main_neighbourhood
    # lastId = int(neighbourhood.houses[-1].id)
    house = House(houseId)
    main_neighbourhood.houses.append(house)


layout = html.Div([
    # hidden div to save data in
    html.Div(id="hidden-div", style={'display': 'none'}),
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


@app.callback(Output('newNeighbourhoodInput', 'style'), [Input("btnNewNeighbourhood", "n_clicks")])
def showNewNeighbourhoodInput(n):
    if n == 1:
        return {'display': 'block'}
    return {"display": "none"}

# Saves neighbourhood in hidden div on main page, so the output div can update on multiple other events


@app.callback(Output('neibourhood_div', 'children'), [Input('upload-data', 'contents')])
def create_house(contents):
    global main_neighbourhood
    root = parse_contents(contents)
    main_neighbourhood = create_neighborhood_object(root)
    nabolag = main_neighbourhood.to_json()
    return html.Div(nabolag)


@app.callback(Output('tabs', 'children'), [Input('neibourhood_div', 'children'), Input('btnCreateNewNeighbourhood', 'n_clicks')], [State('newNeighbourhoodInput', 'value')])
def showNeihbourhood(dictionary, n, value):
    global main_neighbourhood
    if n and n > 0:
        main_neighbourhood = Neighbourhood(value)
    tabs = create_house_tabs(main_neighbourhood)
    return html.Div(children=[
        dcc.Input(id="new_house_id", type='number', style={
            'width': '100'}),
        html.Button("Add house", id="btnAddHouse"),
        dcc.Tabs(id='neighbourhoodTabs', children=tabs),
        html.Div(id='tabs-content', children=["some cool content"])
    ])


@app.callback(Output('initChoices', 'style'), [Input('tabs', 'children')])
def hideButton(children):
    if len(children) > 1:
        return {'display': 'none'}


@app.callback(Output("dropdowndiv", "children"), [Input('neibourhood_div', 'children'), Input('btnNewNeighbourhood', 'n_clicks')])
def fill_dropDown(dictionary, n):
    global main_neighbourhood
    if(dictionary or (n > 0)):
        return dcc.Dropdown(id='user-dropdown', options=[{'label': house.id, 'value': house.id} for house in main_neighbourhood.houses]),


# generate content for tabs
@app.callback(Output('tabs-content', 'children'),
              [Input('neighbourhoodTabs', 'value')])
def render_content(tab):
    global main_neighbourhood
    tabId = int(tab)
    print(tabId)
    if main_neighbourhood is not None:
        house = main_neighbourhood.findHouseById(tabId)
        if house is not None:
            dis = displayHouse(house)
            return html.Div([dis])


@app.callback(Output('neighbourhood-info', 'children'), [Input('tabs', 'children')])
def showNeihbourhoodInfo(children):
    if len(children) > 0:
        global main_neighbourhood
        numOfHouses = 0
        numOfUsers = 0
        numOfDevices = 0
        numOfJobs = 0
        neiId = str(main_neighbourhood.id)
