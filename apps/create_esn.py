import base64
import datetime
import io
import json
import xml.etree.ElementTree as ET
import pandas as pd
import dash
import time
import csv
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.neighbourhood import Neighbourhood, House, Device, Event, User
from app import app
from util.input_utils import prediction_profile_from_csv
from definitions import ROOT_DIR

#Global variables. This makes the app works in a localhost environment only
main_neighbourhood = None
active_house = None
active_device = None

#Resets all global variables
@app.callback(Output('reset', 'children'), [Input('initChoices', 'children')])
def reset_globals(c):
    global main_neighbourhood
    global active_house
    global active_device
    main_neighbourhood = None
    active_house = None
    active_device = None

"""--- START Functions to render a view for the Neighbourhood ---"""

def create_house_tab(house):
    return (dcc.Tab(label='House Id: ' + str(house.id), value=str(house.id)))


def create_house_tabs(nei):
    houses = []
    for house in nei.houses:
        houses.append(create_house_tab(house))
    return houses


def create_house_view(house):
    if len(house.users[0].devices) < 1:
        return []
    content = []
    for user in house.users:
        for device in user.devices:
            content.append(
                html.Tr([
                    html.Td(device.id),
                    html.Td(device.name),
                    html.Td(device.template),
                    html.Td(device.type)
                ])
            )

    return content

def create_jobs_list(house):
    jobs=[]
    for device in house.users[0].devices:
        for event in device.events:
            jobs.append(
                html.Tr([
                    html.Td(event.device.name),
                    html.Td(event.unixToString(event.timestamp)),
                    html.Td(event.unixToString(event.est)),
                    html.Td(event.unixToString(event.lst))
                ])
            )
    return jobs

def displayHouse(house):
    if len(house.users[0].devices) < 1:
        return html.Div(className="house_content_empty", children=["This house is empty"])
    return html.Div([
                    html.Table(className="house_content_table", children=[
                        html.Tr([ #TableRow with tableheaders
                            html.Th("DEVICE ID"),
                            html.Th("NAME"),
                            html.Th("TEMPLATE"),
                            html.Th("TYPE")
                        ])] +
                        create_house_view(house)
                    ),
                     html.H5(className="tabcontent_header", children=["Jobs in house:"]),
                     html.Table(className="house_content_table", children=[
                         html.Tr([ #TableRow with tableheaders
                             html.Th("DEVICE"),
                             html.Th("TIME"),
                             html.Th("EST"),
                             html.Th("LST")
                         ])] + 
                         create_jobs_list(house)
                     )
                     ])


@app.callback(Output('tabs', 'children'),
              [Input('neighbourhood_div', 'children')])
def neighbourhood_tab_view(dictionary):
    global main_neighbourhood
    if main_neighbourhood is not None:
        tabs = create_house_tabs(main_neighbourhood)
        return html.Div(children=[
            dcc.Tabs(id='neighbourhoodTabs',
                     children=tabs),
            html.Div(id='tabs_content')])


@app.callback(Output('tabs_content', 'children'),
              [Input('neighbourhoodTabs', 'value'),
              Input('save_job', 'n_clicks'),
              Input('jobsXML', 'contents')])
def render_content(value, n, contents):
    global main_neighbourhood
    global active_house
    if n and n>0 or contents is not None:
        tabId = int(active_house.id)
    if value is not None:
        tabId = int(value)
    elif main_neighbourhood is not None:  # get the id of first house in houselist
        tabId = int(main_neighbourhood.houses[0].id)
    if main_neighbourhood is not None:
        house = main_neighbourhood.findHouseById(tabId)
        if house is not None:
            dis = displayHouse(house)
            return html.Div([dis])



"""--- END Functions to render a view for the Neighbourhood ---"""

def addHouseToNeighbourhood(houseId):
    global main_neighbourhood
    house = House(houseId)
    main_neighbourhood.houses.append(house)

#Modal which runs all the time, but are shown when user clicks on "Configure house" button
def configHouseModal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # header
                        html.Div(
                            [
                                html.Span(
                                    "Configure devices",
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
                        dcc.Tabs(id="configHouseTabs", value='addNewConsumer', children=[
                            dcc.Tab(label='Configure a device',
                                    value="configHouseDevice"),
                            dcc.Tab(label='Add new consumer',
                                    value="addNewConsumer"),
                            dcc.Tab(label='Add new producer',
                                    value='addNewProducer')
                        ]),
                        # form
                        html.Div(id='configHouse-content', children=[
                            dcc.Input(id="newDeviceId"),
                            dcc.Input(id="newDeviceName"),
                            dcc.Input(id="newDeviceTemplate"),
                            dcc.Dropdown(id="newDeviceType"),
                            dcc.Upload(id="weather1"),
                            dt.DataTable(id="w1dt", rows=[{'Time': [], 'Value': []}]),
                            dcc.Upload(id="weather2"),
                            dt.DataTable(id="w2dt", rows=[{'Time': [], 'Value': []}]),
                            dcc.Upload(id="weather3"),
                            dt.DataTable(id="w3dt", rows=[{'Time': [], 'Value': []}]),
                            dcc.Upload(id="weather4"),
                            dt.DataTable(id="w4dt", rows=[{'Time': [], 'Value': []}]),
                            dcc.Upload(id="LoadPredictionUpload"),
                            dt.DataTable(id="loadOrPredictionTable", rows=[{'Time': [], 'Value': []}])
                        ]),
                        html.Button(
                            "Save",
                            id="save_consumer",
                            n_clicks_timestamp='0',
                        ),
                        html.Button(
                            "Save",
                            id="save_producer",
                            n_clicks_timestamp='0',
                        ),
                        html.Button("Delete device", id='btnDeleteDevice', n_clicks_timestamp='0')
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

#Modal which runs all the time, but are shown when user clicks on "Add job" button
def addJobModal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # header
                        html.Div(
                            [
                                html.Span(
                                    "Add Job",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="job_modal_close",
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

                        html.Div(id='addJobs-content', children=[
                            dcc.Dropdown(id='jobs_device_dropdown'),
                            dcc.DatePickerSingle(id='estDatePicker'),
                            dcc.Input(id='estTimePicker'),
                            dcc.DatePickerSingle(id='lstDatePicker'),
                            dcc.Input(id='lstTimePicker')
                        ]),
                        html.Button(
                            "Save",
                            id="save_job",
                            n_clicks_timestamp='0',
                            className="button button--primary add"
                        ),
                        html.Button("Delete")
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="job_modal",
        style={"display": "none"},
    )

"""
Layout for create_esn app. 
Uses the hidden-div solution to create callbacks when adding content
"""
layout = html.Div([
    html.Div(id="save_hidden", style={'display': 'none'}),
    html.Div(id="reset", style={'display': 'none'}),
    # hidden div to save data in
    html.Div(id='save_jobs', style={'display': 'none'}),
    html.Div(id='save_jobs_fromxml', style={'display': 'none'}),
    html.Div(id="consumer_div", style={'display': 'none'}),
    html.Div(id="producer_div", style={'display': 'none'}),
    html.Div(id='nInfo', children=[
        html.Div('nabolag: ' + str(main_neighbourhood),
                 id="main_neighbourhood-info"),
        html.Div('hus: ' + str(type(active_house)), id="active_house-info"),
        html.Div('device: ' + str(active_device), id="active_device-info"),
        html.Div('device:', id='deviceTwo')
    ],
             style={'display': 'none'}),
    html.H4("Create a new neighbourhood"),
    html.Div(id="initChoices", children=[
        html.Button("Create new from scratch", id="btnNewNeighbourhood", n_clicks_timestamp='0'),
        dcc.Upload(id="upload-data", children=[html.Button("Create new from XML")]),
        html.Div(id="newNeighbourhoodInput", children=[
            dcc.Input(id="newNeighbourhoodId", value=0, type="number", style={
                'width': '50px'
            }),
            html.Button("Create Neighbourhood",
                        id="btnCreateNewNeighbourhood", n_clicks_timestamp='0')
        ],
                 style={'display': 'none'}),
    ]),
    html.Div(id="newHouseInput", children=[
        html.Button("Add house", id="btnAddHouse", n_clicks_timestamp='0'),
        html.Button("Delete house", id="btnDeleteHouse",
                    n_clicks_timestamp='0'),
        html.Button("Add or config device", id="btnConfigHouse",
                    n_clicks_timestamp='0'),
        html.Button("Add job", id="btnAddJob", n_clicks_timestamp='0'),
        dcc.Upload(id='jobsXML', children=[html.Button("Add jobs from XML")])],
             style={'display': 'none'}),
    html.Div(id="neighbourhood-info"),
    html.Div(id="tabs", children=[
        dcc.Tabs(id='neighbourhoodTabs',
                     children=[dcc.Tab()]),
            html.Div(id='tabs_content')
    ]),
    html.Div(id='saveNeighbourhood', children=[
        dcc.Input(id="neighbourhoodName", placeholder="neighbourhoodName"),
        html.Button("Save Neighbourhood", id="btnSaveNeighbourhood"),
        html.Div(id="saveNeighbourhoodFeedback", children=["Neighbourhood added to your input folder!"], style={'display':'none'}),
    ],
             style={'display': 'none'}),

    configHouseModal(),
    addJobModal()
], className="create_esn_div")


# takes in a xmlfile and returns a XML Elementree of the neighborhood.

"""--- START functions to parse xml and csv files for user input and create python objects/list of them ---"""
def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'xml' in content_type:
            decoded = base64.b64decode(content_string)
            root = ET.fromstring(decoded)
            return root


def create_neighborhood_object(treeroot):
    if treeroot is not None:
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

def create_loads_list(jobsroot):
    if jobsroot is not None:
        global main_neighbourhood
        for house in jobsroot:
            h = main_neighbourhood.findHouseById(int(house.get('id')))
            if h is not None:
                for user in house:
                    for device in user:
                        d_id = device.find('id').text
                        d = h.findDeviceById(int(d_id))
                        if d is not None:
                            timestamp =device.find('creation_time').text
                            est=device.find('est').text
                            lst=device.find('lst').text
                            d.events.append(Event(d, int(timestamp), int(est), int(lst)))



def parse_csv(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)  # decoded is now bytes
        string = io.StringIO(decoded.decode('utf-8'))
        timestamps = []
        values = []
        for line in string:
            if line is not "":
                split_line = line.split(" ")
                timestamps.append(split_line[0])
                values.append(split_line[1].rstrip())
        output = [('Time', timestamps),
                  ('Value', values)]
        df = pd.DataFrame.from_dict(dict(output))
        return df


"""--- END functions to parse xml and csv files for user input and create python objects of them ---"""


@app.callback(Output('save_jobs_fromxml', 'children'), [Input('jobsXML', 'contents')])
def createJobList(contents):
    root = parse_contents(contents)
    create_loads_list(root)

# Saves neighbourhood in hidden div on main page, so the output div can update on multiple other events
# Function to store and update main neighbourhood div / Controller


@app.callback(Output('consumer_div', 'children'),
              [Input('save_consumer', 'n_clicks_timestamp')],
              [
                  State('newDeviceId', 'value'),
                  State('newDeviceName', 'value'),
                  State('newDeviceTemplate', 'value'),
                  State('newDeviceType', 'value'),
                  State('loadOrPredictionTable', 'rows')
              ])
def addConsumer(n, dId, dName, dTemp, dType, rows):
    global active_house
    global active_device
    if (dId or dName or dTemp or dType) is not None:
        dev = Device(dId, dName, dTemp, dType)
        dev.loadProfile = pd.DataFrame(rows) if rows is not None else None
        if active_device is None:
            active_house.users[0].devices.append(dev)
        elif active_device is not None:
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
    return html.Div('hello')


@app.callback(Output('producer_div', 'children'),
              [Input('save_producer', 'n_clicks_timestamp')],
              [
                  State('newDeviceId', 'value'),
                  State('newDeviceName', 'value'),
                  State('newDeviceTemplate', 'value'),
                  State('newDeviceType', 'value'),
                  State('w1dt', 'rows'),
                  State('w2dt', 'rows'),
                  State('w3dt', 'rows'),
                  State('w4dt', 'rows'),
              ])
def configProducer(n, dId, dName, dTemp, dType, w1, w2, w3, w4):
    global main_neighbourhood
    global active_house
    global active_device
    if (dId or dName or dTemp or dType) is not None:
        dev = Device(dId, dName, dTemp, dType)
        dev.weatherPredictions1 = pd.DataFrame(w1) if w1 is not None else None
        dev.weatherPredictions2 = pd.DataFrame(w2) if w2 is not None else None
        dev.weatherPredictions3 = pd.DataFrame(w3) if w3 is not None else None
        dev.weatherPredictions4 = pd.DataFrame(w4) if w4 is not None else None
        if active_device is None:
            active_house.users[0].devices.append(dev)
        elif active_device is not None:
            main_neighbourhood.findHouseById(active_house.id)
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
        return html.Div(str(dev.weatherPredictions1))
    return html.Div("hello")

"""
This function does most of the logic when adding and removing houses,devices, jobs to the neighbourhood
Updates the main_neighbourhood
"""

@app.callback(Output('neighbourhood_div', 'children'),
              [
                  Input('upload-data', 'contents'),
                  Input('btnNewNeighbourhood', 'n_clicks_timestamp'),
                  Input('btnAddHouse', 'n_clicks_timestamp'),
                  Input('btnDeleteHouse', 'n_clicks_timestamp'),
                  Input('save_consumer', 'n_clicks_timestamp'),
                  Input('save_producer', 'n_clicks_timestamp'),
                  Input('btnDeleteDevice', 'n_clicks_timestamp')
              ])
def configure_neighbourhood(contents, btnNewNei, btnAddHouse, btnRemoveHouse, btnSaveCons, btnSaveProd,
                            btnDeleteDevice):
    global main_neighbourhood
    global active_house
    global active_device
    # finds the button which was pressed last
    btnclicks = [btnNewNei, btnAddHouse, btnRemoveHouse, btnSaveCons, btnSaveProd, btnDeleteDevice]
    btnclicks.sort(key=int)
    # Actions for the different buttons
    if btnNewNei != '0' and btnNewNei == btnclicks[-1]:
        newHouse = House(1)
        newHouse.users.append(User(1))
        main_neighbourhood = Neighbourhood(1)
        main_neighbourhood.houses.append(newHouse)
        active_house = main_neighbourhood.houses[0]
    elif btnAddHouse != '0' and btnAddHouse == btnclicks[-1]:
        i = main_neighbourhood.nextHouseId()
        newHouse = House(i)
        newHouse.users.append(User(1))
        main_neighbourhood.houses.append(newHouse)
    elif btnRemoveHouse != '0' and btnRemoveHouse == btnclicks[-1]:
        i = main_neighbourhood.houses.index(active_house)
        main_neighbourhood.houses.remove(active_house)
    elif (btnSaveCons != '0' or btnSaveProd != '0') and (btnSaveCons or btnSaveProd) == btnclicks[-1]:
        pass  # needed to take this functionality and move it to addDevice function. See line 336.
    elif btnDeleteDevice != '0' and btnDeleteDevice == btnclicks[-1]:
        active_house.users[0].devices.remove(active_device)
    elif main_neighbourhood is None and contents is not None: #This will only fire the first time xml contens are loaded
        root = parse_contents(contents)
        main_neighbourhood = create_neighborhood_object(root)
        active_house = main_neighbourhood.houses[0]
    if main_neighbourhood is not None:
        nabolag = main_neighbourhood.to_json()
        return html.Div(nabolag)
    else:
        return html.Div()


""" --- Start functions to show change the style to different divs and modals ---"""
def show(n, contents):
    if (n and n > 0) or contents:
        return {'display': 'flex'}
    return {'display':'none'}

@app.callback(Output('newHouseInput', 'style'),
              [Input('btnNewNeighbourhood', 'n_clicks'), Input('upload-data', 'contents')])
def showMenu(n, contents):
    return show(n, contents)


@app.callback(Output('saveNeighbourhood', 'style'),
              [Input('btnNewNeighbourhood', 'n_clicks'), Input('upload-data', 'contents')])
def showSaveButton(n, contents):
    return show(n, contents)


@app.callback(Output('initChoices', 'style'), [Input('tabs', 'children')])
def hideButton(children):
    if children and len(children) > 1:
        return {'display': 'none'}

@app.callback(Output("house_modal", "style"), [Input("btnConfigHouse", "n_clicks")])
def display_leads_modal_callback(n):
    if n and n > 0:
        global active_device
        active_device = None
        return {"display": "block"}
    return {"display": "none"}

@app.callback(
    Output("btnConfigHouse", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"),
     Input("save_consumer", "n_clicks"),
     Input("save_producer", "n_clicks"),
     Input('btnDeleteDevice', 'n_clicks')]
)
def close_modal_callback(n, n2, n3, n4):
    return 0


@app.callback(
    Output("btnAddJob", "n_clicks"),
    [Input("job_modal_close", "n_clicks"),
     Input("save_job", "n_clicks")],
)
def close_jobModal_callback(n, n2):
    return 0


@app.callback(Output('job_modal', 'style'), [Input('btnAddJob', 'n_clicks')])
def displayJobModal(n):
    if (n and n > 0):
        return {'display': 'block'}
    return {'display':'none'}

""" --- END functions to show change the style to different divs and modals ---"""
# Function to update the view based on neighbourhood div



"""--- START Callback functions to render input fields based on which type of device the user want to change---"""

@app.callback(Output('addJobs-content', 'children'), [Input('job_modal', 'style')])
def renderAddJobContent(style):
    global active_house
    if style == {"display": "block"}:
        return html.Div(id='addJob', children=[
            html.Div(id='addJobContent'),
            dcc.Dropdown(id='jobs_device_dropdown', placeholder='Choose device',
                         options=[{'label': device.name, 'value': device.id}
                                  for user in active_house.users for device in user.devices]),
            html.H4("Earliest Start time"),
            dcc.DatePickerSingle(
                id='estDatePicker',
                initial_visible_month=datetime.now()

            ),
            html.Br(),
            dcc.Input(
                id='estTimePicker',
                type='time',
                placeholder='HH:MM'
            ),
            html.H4("Latest start time"),
            dcc.DatePickerSingle(
                id='lstDatePicker',
                initial_visible_month=datetime.now()
            ),
            html.Br(),
            dcc.Input(
                id='lstTimePicker',
                type='time',
                placeholder='HH:MM'
            )
        ]),

def create_producer_modal_form(did, name, temp, devtype, w1, w2, w3, w4):
    return html.Div(className="producer_modal_form", children=[
            html.Div(className="devId", children=[
                html.Div("Device ID:"),
                dcc.Input(id="newDeviceId", type="number", value=did, className="modal_input_field")
            ]),
            html.Div(className="devName", children=[
                html.Div("Device Name:"),
                dcc.Input(id="newDeviceName", type="text", placeholder="", value=name, className="modal_input_field")
            ]),
            html.Div(className="devTemp", children=[
                html.Div("Device Template:"),
                dcc.Input(id="newDeviceTemplate", type="number", placeholder="template", value=temp, className="modal_input_field")
            ]),
            html.Div(className="devType", children=[
                html.Div("Device Type:"),
                dcc.Dropdown(id="newDeviceType",
                         options=[{'label': "Producer", 'value': "producer"}],
                         value=devtype)
            ]),
            html.Div(className="pv1", children=[
                dcc.Upload(id="weather1", className="w1Pred", children=[html.Button('First Predition')]),
                dt.DataTable(id="w1dt", rows=w1)
            ]),
            html.Div(className="pv2", children=[
                dcc.Upload(id="weather2", className="w2Pred", children=[html.Button('Second Predition')]),
                dt.DataTable(id="w2dt", rows=w2),
            ]),
            html.Div(className="pv3", children=[
                dcc.Upload(id="weather3", className="w3Pred", children=[html.Button('Third Prediction')]),
                dt.DataTable(id="w3dt", rows=w3),
            ]),
            html.Div(className="pv4", children=[
                dcc.Upload(id="weather4", className="w4Pred", children=[html.Button('Fourth Prediction')]),
                dt.DataTable(id="w4dt", rows=w4)
            ])
        ])

def create_consumer_modal_form(did, name, temp, dtype, load):
    return html.Div(className="consumer_modal_form", children=[
            html.Div(className="devId", children=[
                html.Div("Device ID:"),
                dcc.Input(id="newDeviceId", type="number", value=did, className="modal_input_field")
            ]),
            html.Div(className="devName", children=[
                html.Div("Device Name:"),
                dcc.Input(id="newDeviceName", type="text", value=name, className="modal_input_field")
            ]),
            html.Div(className="devTemp", children=[
                html.Div("Device Template:"),
                dcc.Input(id="newDeviceTemplate", type="number", value=temp, className="modal_input_field")
            ]),
            html.Div(className="devType", children=[
                html.Div("Device Type:"),
                dcc.Dropdown(id="newDeviceType",
                         options=[{'label': "Consumer", 'value': "consumer"}],
                         value=dtype)
            ]),
            dcc.Upload(id="LoadPredictionUpload", className="devLoad", children=[html.Button('Add load csv file')]),
            html.Div(className="loadTable", children=[
                dt.DataTable(id="loadOrPredictionTable", rows=load)
            ])
        ])

@app.callback(Output('configHouse-content', 'children'), [Input('configHouseTabs', 'value')])
def showHouseConfigContent(value):
    global active_house
    global active_device
    empty_p = [{'Time': [], 'Value': []}]
    if value == 'configHouseDevice':
        return html.Div([
            dcc.Dropdown(id='user-device-dropdown', options=[{'label': device.name, 'value': device.id}
                                                             for user in active_house.users for device in user.devices],
                         placeholder='Select device'),
            html.Div(id="deviceConfigForm")
        ])
    elif value == 'addNewConsumer':
        active_device = None
        return create_consumer_modal_form(0, "", 0, "consumer", empty_p)
    elif value == 'addNewProducer':
        active_device = None
        return create_producer_modal_form(0, "", 0, "producer", empty_p, empty_p, empty_p, empty_p)

@app.callback(Output('deviceConfigForm', 'children'), [Input('active_device-info', 'children')])
def renderConfigForm(children):
    empty_p = [{'Time': [], 'Value': []}]
    if active_device is not None:
        if active_device.type== "consumer":
            l = empty_p if active_device.loadProfile is None else active_device.loadProfile.to_dict('records')
            return create_consumer_modal_form(active_device.id, active_device.name, active_device.template, active_device.type, l)
        
        elif active_device.type == 'producer':
            pv1 = empty_p if active_device.weatherPredictions1 is None else active_device.weatherPredictions1.to_dict('records')
            pv2 = empty_p if active_device.weatherPredictions2 is None else active_device.weatherPredictions2.to_dict('records')
            pv3 = empty_p if active_device.weatherPredictions3 is None else active_device.weatherPredictions3.to_dict('records')
            pv4 = empty_p if active_device.weatherPredictions4 is None else active_device.weatherPredictions4.to_dict('records')
            return create_producer_modal_form(active_device.id, active_device.name, active_device.template, active_device.type, pv1, pv2, pv3, pv4)

@app.callback(Output('save_consumer', 'style'), [Input('configHouseTabs', 'value'), Input('active_device-info', 'children')])
def toggle_save_button(v1, c):
    if v1 == 'configHouseDevice':
        if active_device is not None and active_device.type== "consumer":
            return {'display':'inline-block'}
    if v1 == 'addNewConsumer':
        return {'display':'inline-block'}
    else:
        return {'display':'none'}



@app.callback(Output('save_producer', 'style'), [Input('configHouseTabs', 'value'), Input('active_device-info', 'children')])
def toggle_save_prod_button(v1, c):
    if v1 == 'configHouseDevice':
        if active_device is not None and active_device.type== "producer":
            return {'display':'inline-block'}
    if v1 == 'addNewProducer':
        return {'display':'inline-block'}
    else:
        return {'display':'none'}



"""--- END Callback functions to render input fields based on which type of device the user want to change---"""

"""---START functions to update dash DataTable based on inputs from user ---"""


@app.callback(Output('loadOrPredictionTable', 'rows'), [Input('LoadPredictionUpload', 'contents')],
              [State('LoadPredictionUpload', 'filename')])
def update_table(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict('records')
    elif active_device and active_device.loadProfile is not None:
        if len(active_device.loadProfile['Time'].iloc[0]) > 0:
            return active_device.loadProfile.to_dict('records')
    else:
        return [{'Time': [], 'Value': []}]

@app.callback(Output('w1dt', 'rows'), [Input('weather1', 'contents')], [State('weather1', 'filename')])
def update_w1(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict('records')
    elif active_device and active_device.weatherPredictions1 is not None:
        if len(active_device.weatherPredictions1['Time'].iloc[0]) > 0:
            return active_device.weatherPredictions1.to_dict('records')
    else:
        return [{'Time': [], 'Value': []}]



@app.callback(Output('w2dt', 'rows'), [Input('weather2', 'contents')], [State('weather2', 'filename')])
def update_w2(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict('records')
    elif active_device and active_device.weatherPredictions2 is not None:
        if len(active_device.weatherPredictions2['Time'].iloc[0]) > 0:
            return active_device.weatherPredictions2.to_dict('records')
    else:
        return [{'Time': [], 'Value': []}]



@app.callback(Output('w3dt', 'rows'), [Input('weather3', 'contents')], [State('weather3', 'filename')])
def update_w3(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict('records')
    elif active_device and active_device.weatherPredictions3 is not None:
        if len(active_device.weatherPredictions3['Time'].iloc[0]) > 0:
            return active_device.weatherPredictions3.to_dict('records')
    else:
        return [{'Time': [], 'Value': []}]



@app.callback(Output('w4dt', 'rows'), [Input('weather4', 'contents')], [State('weather4', 'filename')])
def update_w4(contents, filename):
    global active_device
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict('records')
    elif active_device and active_device.weatherPredictions4 is not None:
        if len(active_device.weatherPredictions4['Time'].iloc[0]) > 0:
            return active_device.weatherPredictions4.to_dict('records')
    else:
        return [{'Time': [], 'Value': []}]

"""---END functions to update dash DataTable based on inputs from user ---"""

"""--function for debugging --
@app.callback(Output('nInfo', 'children'), [Input('neighbourhood_div', 'children')])
def showNid(children):
    global main_neighbourhood
    global active_house
    return html.Div([
        html.Div('nabolag: ' + str(len(main_neighbourhood.houses)),
                 id="main_neighbourhood-info"),
        html.Div('hus: ' + str(type(active_house)), id="active_house-info"),
        html.Div('device: ' + str(type(active_device)), id="active_device-info"),
        html.Div('device: ' + str(type(active_device)), id="deviceTwo"),
    ])
"""

# set active house.
"""--- Start Functions to set the global variables when interacting with the GUI---"""

@app.callback(Output('active_house-info', 'children'), [Input('neighbourhoodTabs', 'value')])
def setActiveHouse(value):
    global active_house
    global main_neighbourhood
    if value is not None:
        active_house = main_neighbourhood.findHouseById(int(value))
    return html.Div(str(type(active_house)))

def set_active_device(value):
    global active_house
    global active_device
    if value is not None:
        active_device = active_house.findDeviceById(int(value))
    return html.Div(str(type(active_device)))

@app.callback(Output('active_device-info', 'children'), [Input('user-device-dropdown', 'value')])
def setActiveDevice(value):
    return set_active_device(value)

@app.callback(Output('deviceTwo', 'children'), [Input('jobs_device_dropdown', 'value')])
def setADevice(value):
    return set_active_device(value)

"""--- END Functions to set the global variables when interacting with the GUI---"""

# Change tab on delete
'''
@app.callback(Output('neighbourhoodTabs', 'value'), [Input('btnDeleteHouse', 'n_clicks_timestamp')])
def tabChangeOnDelete(a):
    if (a and int(a) > 0) and main_neighbourhood is not None:
        return str(main_neighbourhood.houses[0].id)
'''
#Function to add Jobs to specific devices
@app.callback(Output('save_jobs', 'children'),
              [Input('save_job', 'n_clicks')],
              [
                  State('estDatePicker', 'date'),
                  State('estTimePicker', 'value'),
                  State('lstDatePicker', 'date'),
                  State('lstTimePicker', 'value')
              ]
              )
def saveJobs(n, estDate, estTime, lstDate, lstTime):
    if n and n > 0:
        global active_house
        global active_device
        if (estDate, estTime, lstDate, lstTime) is not None:
            est = createEpochTime(estDate, estTime)
            lst = createEpochTime(lstDate, lstTime)
            timeAdded = int(time.time())
        if active_device.type == 'consumer':
            active_device.events.append(Event(active_device, timeAdded, est, lst))
            job = str(timeAdded) + ';' + str(est) + ';' + str(lst) + ';[' + str(active_house.id) + ']:[' + str(
                active_device.id) + '];' + str(active_device.id) + '.csv'
            #active_device.events.append(job)


def createEpochTime(date, time):
    d = date.split('-')
    t = time.split(':')
    dateTime = datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1])).timestamp()
    return int(dateTime)

def create_pv_csv_files(filepath, prediction, house, device, n):
    prediction.to_csv(filepath + "/predictions/" + str(house.id) + "_" + str(device.id) + "_"+str(n)+".csv", sep=" ", index=False, header=False)
    return '{};pv_producer[{}]:[{}];{}_{}_{}.csv'.format(prediction['Time'].iloc[0], house.id, device.id, house.id, device.id, n)

def create_consumer_csv_files(event, house):
    return '{};{};{};[{}]:[{}]:[{}];{}.csv'.format(str(event.timestamp), str(event.est), str(event.lst), str(house.id), str(event.device.id), str(event.device.id), str(event.device.id)) #Maybe include templatenumber?

#Function to create files for simulation.
@app.callback(Output('save_hidden', 'children'),
              [Input('btnSaveNeighbourhood', 'n_clicks')],
              [State('neighbourhoodName', 'value')])
def save_neighbourhood(n, value):
    global main_neighbourhood
    if n and n > 0:
        if value is None:
            value = 'no_name'
        filepath = ROOT_DIR + "/input/" + value
        os.makedirs(filepath)
        os.makedirs(filepath + "/loads")
        os.makedirs(filepath + "/predictions")
        producer_events = []
        consumer_events =[]
        # make dir loads, prediction, consumerevent.csv, produserevent.csv
        for house in main_neighbourhood.houses:
            for device in house.users[0].devices:  # only one user in each house
                if device.type == "producer":
                    if device.weatherPredictions1 is not None and len(device.weatherPredictions1['Time'].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weatherPredictions1, house, device, 1))
                    if device.weatherPredictions2 is not None and len(device.weatherPredictions2['Time'].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weatherPredictions1, house, device, 2))
                    if device.weatherPredictions3 is not None and len(device.weatherPredictions3['Time'].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weatherPredictions1, house, device, 3))
                    if device.weatherPredictions4 is not None and len(device.weatherPredictions4['Time'].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weatherPredictions1, house, device, 4))
                elif device.type == "consumer":
                    if device.loadProfile is not None and len(device.loadProfile['Time'].iloc[0]) > 0:
                        device.loadProfile.to_csv(filepath + "/loads/" + str(device.id) + ".csv", sep=" ", index=False,
                                                  header=False)
                    for event in device.events:
                        consumer_events.append(create_consumer_csv_files(event, house))
        with open(filepath + '/consumer_event.csv', 'a+') as consumerJobscsv:
            wr = csv.writer(consumerJobscsv, delimiter='\n')
            wr.writerow(consumer_events)
        with open(filepath + '/producer_event.csv', 'a+') as producerJobscsv:
            wr = csv.writer(producerJobscsv, delimiter='\n')
            wr.writerow(producer_events)

        # pickle neighbourhood object and save it locally?

@app.callback(Output('saveNeighbourhoodFeedback', 'style'), [Input('btnSaveNeighbourhood', 'n_clicks')])
def give_save_feedback(n):
    if n and n>0:
        return {'display':'block'}
    return {'display':'none'}