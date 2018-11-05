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
from backend.neighbourhood import Neighbourhood
from backend.house import House
from backend.device import Device
from backend.user import User
from app import app
from util.input_utils import prediction_profile_from_csv
from definitions import ROOT_DIR

main_neighbourhood = None
active_house = None
active_device = None
addedLoads = []

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
                    html.Span("DeviceID: " + str(device.id) + "\t\t"),
                    html.Span("DeviceName: " + device.name + "\t\t"),
                    html.Span("DeviceTemplate: " + str(device.id) + "\t\t"),
                    html.Span("DeviceType: " + device.type + "\t\t"),
                ])
            )
        content.append(html.Div(children=[
                        html.H4("Jobs list here")
                    ]))
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
                     html.Br(),
                     html.Span("Number of devices: " + str(numOfDevices)),
                     html.Div(children=create_house_view(house)),
                     ])


def addHouseToNeighbourhood(houseId):
    global main_neighbourhood
    # lastId = int(neighbourhood.houses[-1].id)
    house = House(houseId)
    main_neighbourhood.houses.append(house)


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
                        dcc.Tabs(id="configHouseTabs", value='configHouseDevice', children=[
                            dcc.Tab(label='Configure a device',
                                    value="configHouseDevice"),
                            dcc.Tab(label='Add new consumer',
                                    value="addNewConsumer"),
                            dcc.Tab(label='Add new producer',
                                    value='addNewProducer')
                        ]),
                        # form
                        html.Div(id='configHouse-content'),
                        html.Span(
                            "Save cons",
                            id="save_consumer",
                            n_clicks_timestamp='0',
                            className="button button--primary add"
                        ),
                        html.Span(
                            "Save prod",
                            id="save_producer",
                            n_clicks_timestamp='0',
                            className="button button--primary add"
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

                        html.Div(id='addJobs-content'),
                        html.Span(
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


layout = html.Div([
    html.Div(id="save_hidden", style={'display': 'none'}),
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
    style={'display':'none'}),
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
        html.Button("Configure house", id="btnConfigHouse",
                    n_clicks_timestamp='0'),
        html.Button("Add job", id="btnAddJob", n_clicks_timestamp='0'),
        dcc.Upload(id='jobsXML', children=[html.Button("Add jobs from XML")])
    ],
    style={'display':'none'}
    ),
    html.Div(id="neighbourhood-info"),
    html.Div(id="tabs"),
    html.Div(id='saveNeighbourhood', children=[
        dcc.Input(id="neighbourhoodName", placeholder="neighbourhoodName"),
        html.Button("Save Neighbourhood", id="btnSaveNeighbourhood"),
    ],
    style={'display':'none'}),
    configHouseModal(),
    addJobModal()
])

# takes in a xmlfile and returns a XML Elementree of the neighborhood.


def parse_contents(contents):
    if contents is not None:
        content_type, content_string=contents.split(',')
        if 'xml' in content_type:
            decoded=base64.b64decode(content_string)
            root=ET.fromstring(decoded)
            return root


def create_neighborhood_object(treeroot):
    nabolag=Neighbourhood(int(treeroot.get("id")))
    for house in treeroot:
        h=House(int(house.get("id")))
        for user in house:
            u=User(int(user.get("id")))
            for device in user:
                d=Device(int(device.find("id").text), device.find("name").text, int(
                    device.find("template").text), device.find("type").text)
                u.devices.append(d)
            h.users.append(u)
        nabolag.houses.append(h)
    return nabolag

def create_loads_list(jobsroot):
    global addedLoads
    for house in jobsroot:
        for user in house:
            for device in user:
                jobString = str(device.find('creation_time').text)+';'+ str(device.find('est').text) + ';' + str(device.find('lst').text)+ ';[' + str(house.get('id'))+'];[' + str(device.find('id').text)+'];'+str(device.find('profile').text) +'.csv'
                addedLoads.append(jobString)
                
@app.callback(Output('save_jobs_fromxml', 'children'), [Input('jobsXML', 'contents')])
def createJobList(contents):
    root = parse_contents(contents)
    create_loads_list(root)

"""
Callback function to toggle the xml input field
"""

def create_neighborhood_html(neighborhood):
    htmlString="<div>"
    htmlString += "Nabolag:"
    houses=[]
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
        dev=Device(dId, dName, dTemp, dType)
        dev.loadProfile = pd.DataFrame(rows) if rows is not None else None
        if active_device is None:
            active_house.users[0].devices.append(dev)
        elif active_device is not None:
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
    return html.Div(str(dev.loadProfile))

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
    global active_house
    global active_device
    if (dId or dName or dTemp or dType) is not None:
        dev=Device(dId, dName, dTemp, dType)
        print(type(w1[0]['Time']))
        if w1 and bool(w1[0]):
            dev.weatherPredictions1 = pd.DataFrame(w1)
            event = w1[0]['Time'] + ';pv_producer[' + str(active_house.id) +']:['+str(dev.id)+'];'+str(active_house.id)+"_"+str(dev.id)+'_1.csv'
            dev.events.append(event)
        if w2 and bool(w2[0]):
            dev.weatherPredictions2 = pd.DataFrame(w2)
            event = w2[0]['Time'] + ';pv_producer[' + str(active_house.id) +']:['+str(dev.id)+'];'+str(active_house.id)+"_"+str(dev.id)+'_2.csv'
            dev.events.append(event)
        if w3 and bool(w3[0]):
            dev.weatherPredictions3 = pd.DataFrame(w3)
            event = w3[0]['Time'] + ';pv_producer[' + str(active_house.id) +']:['+str(dev.id)+'];'+str(active_house.id)+"_"+str(dev.id)+'_3.csv'
            dev.events.append(event)
        if w4 and bool(w4[0]):
            dev.weatherPredictions4 = pd.DataFrame(w4)
            event = w4[0]['Time'] + ';pv_producer[' + str(active_house.id) +']:['+str(dev.id)+'];'+str(active_house.id)+"_"+str(dev.id)+'_4.csv'
            dev.events.append(event)
        if active_device is None:
            active_house.users[0].devices.append(dev)
    
        elif active_device is not None:
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
    print(dev.weatherPredictions1)
    return html.Div(str(dev.weatherPredictions1))

'''

'''
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
def configure_neighbourhood(contents, btnNewNei, btnAddHouse, btnRemoveHouse, btnSaveCons, btnSaveProd, btnDeleteDevice):
    global main_neighbourhood
    global active_house
    global active_device
    #finds the button which was pressed last
    btnclicks = [btnNewNei, btnAddHouse, btnRemoveHouse, btnSaveCons, btnSaveProd, btnDeleteDevice]
    btnclicks.sort(key=int)
    #Actions for the different buttons
    if btnNewNei != '0' and btnNewNei == btnclicks[-1]:
        newHouse=House(1)
        newHouse.users.append(User(1))
        main_neighbourhood=Neighbourhood(1)
        main_neighbourhood.houses.append(newHouse)
        active_house = main_neighbourhood.houses[0]
    elif btnAddHouse != '0' and btnAddHouse == btnclicks[-1]:
        i=main_neighbourhood.nextHouseId()
        newHouse=House(i)
        newHouse.users.append(User(1))
        main_neighbourhood.houses.append(newHouse)
    elif btnRemoveHouse != '0' and btnRemoveHouse == btnclicks[-1]:
        i = main_neighbourhood.houses.index(active_house)
        main_neighbourhood.houses.remove(active_house)
    elif (btnSaveCons != '0' or btnSaveProd != '0') and (btnSaveCons or btnSaveProd) == btnclicks[-1]:
        pass #needed to take this functionality and move it to addDevice function. See line 336.
    elif btnDeleteDevice != '0' and btnDeleteDevice == btnclicks[-1]:
        active_house.users[0].devices.remove(active_device)
    elif contents is not None:
        root = parse_contents(contents)
        main_neighbourhood = create_neighborhood_object(root)
        active_house = main_neighbourhood.houses[0]
    if main_neighbourhood is not None:
        nabolag = main_neighbourhood.to_json()
        return html.Div(nabolag)
    else:
        return html.Div()


@app.callback(Output('newHouseInput', 'style'), [Input('btnNewNeighbourhood', 'n_clicks'), Input('upload-data','contents')])
def showMenu(n, contents):
    if n or contents:
        return {'display':'block'}


@app.callback(Output('saveNeighbourhood', 'style'), [Input('btnNewNeighbourhood', 'n_clicks'), Input('upload-data','contents')])
def showSaveButton(n, contents):
    if n or contents:
        return {'display':'block'}


# Function to update the view based on neighbourhood div


@app.callback(Output('tabs', 'children'),
              [Input('neighbourhood_div', 'children')])
def neighbourhood_tab_view(dictionary):
    global main_neighbourhood
    if main_neighbourhood is not None:
        tabs = create_house_tabs(main_neighbourhood)
        return html.Div(children=[
            dcc.Tabs(id='neighbourhoodTabs',
            children=tabs,),
            html.Div(id='tabs-content')])


@app.callback(Output('initChoices', 'style'), [Input('tabs', 'children')])
def hideButton(children):
    if len(children) > 1:
        return {'display': 'none'}

# generate content for tabs


@app.callback(Output('tabs-content', 'children'),
              [Input('neighbourhoodTabs', 'value')])
def render_content(value):
    global main_neighbourhood
    global active_house
    if value is not None:
        tabId = int(value)
    else:  # get the id of first house in houselist
        tabId = int(main_neighbourhood.houses[0].id)
    if main_neighbourhood is not None:
        house = main_neighbourhood.findHouseById(tabId)
        if house is not None:
            dis = displayHouse(house)
            return html.Div([dis])


""" ------------------- configHouseModal callbacks ----------------------"""


@app.callback(Output("house_modal", "style"), [Input("btnConfigHouse", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        global active_device
        active_device = None
        return {"display": "block"}
    return {"display": "none"}
# reset to 0 add button n_clicks property

@app.callback(Output('addJobs-content', 'children'), [Input('job_modal', 'style')])
def renderAddJobContent(style):
    if style == {"display": "block"}:
        return html.Div(id='addJob', children=[
                            html.Div(id='addJobContent'),
                            dcc.Dropdown(id='jobs_device_dropdown', placeholder='Choose device', options=[{'label': device.name, 'value': device.id}
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



@app.callback(Output('configHouse-content', 'children'), [Input('configHouseTabs', 'value')])
def showHouseConfigContent(value):
    global active_house
    global active_device
    if value == 'configHouseDevice':
        return html.Div([
            dcc.Dropdown(id='user-device-dropdown', options=[{'label': device.name, 'value': device.id}
                                                             for user in active_house.users for device in user.devices], placeholder='Select device'),
            html.Div(id="deviceConfigForm")
        ])
    elif value == 'addNewConsumer':
        active_device = None
        return html.Div([
            dcc.Input(id="newDeviceId", type="number", placeholder="DeviceID", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Input(id="newDeviceName", type="text", placeholder="DeviceName", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Input(id="newDeviceTemplate", type="number", placeholder="TemplateName", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Dropdown(id="newDeviceType", placeholder="TemplateType",
                         options=[{'label': "Consumer", 'value': "consumer"}],
                         value='consumer'),
            dcc.Upload(id="LoadPredictionUpload", children=[html.Button('Add load csv file')]),
            html.Div(id=''),
            dt.DataTable(id="loadOrPredictionTable",rows=[{}]) 
        ])
    elif value == 'addNewProducer':
        active_device = None
        return html.Div([
            dcc.Input(id="newDeviceId", type="number", value=0, placeholder="DeviceID", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Input(id="newDeviceName", type="text", value='noName', placeholder="DeviceName", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Input(id="newDeviceTemplate", type="number", value=0, placeholder="TemplateName", style={
                'width': '100px'
            }),
            html.Br(),
            dcc.Dropdown(id="newDeviceType",
                         options=[{'label': "Producer", 'value': "producer"}],
                         value='producer'),
                         
            dcc.Upload(id="weather1", children=[html.Button('Add first weather predition')]),
            dt.DataTable(id="w1dt", rows=[{}]),
            dcc.Upload(id="weather2", children=[html.Button('Add second weather predition')]),
            dt.DataTable(id="w2dt", rows=[{}]),
            dcc.Upload(id="weather3", children=[html.Button('Add third weather predition')]),
            dt.DataTable(id="w3dt", rows=[{}]),
            dcc.Upload(id="weather4", children=[html.Button('Add fourth weather predition')]),
            dt.DataTable(id="w4dt", rows=[{}])
        ])


@app.callback(Output('deviceConfigForm', 'children'), [Input('active_device-info', 'children')])
def renderConfigForm(children):
    if active_device is not None:
        output = [
            dcc.Input(id="newDeviceId", type="number", value=active_device.id, style={
                    'width': '100px'
                }),
                html.Br(),
                dcc.Input(id="newDeviceName", type="text", value=active_device.name, style={
                    'width': '100px'
                }),
                html.Br(),
                dcc.Input(id="newDeviceTemplate", type="number", value=active_device.template, style={
                    'width': '100px'
                }),
                html.Br(),
                dcc.Dropdown(id="newDeviceType", value=active_device.type,
                            options=[{'label': "Consumer", 'value': "consumer"}, {'label': "Producer", 'value': "producer"}]),
        ]
        if active_device.type == 'consumer':
            output.extend([
                dcc.Upload(id="LoadPredictionUpload", children=[html.Button('Add load csv file')]),
                dt.DataTable(id="loadOrPredictionTable", rows=[{'Time':[], 'Value':[]}]) if active_device.loadProfile is None else dt.DataTable(id="loadOrPredictionTable", rows=active_device.loadProfile.to_dict('records')),
            ])
        if active_device.type == 'producer':
            output.extend([
                dcc.Upload(id="weather1", children=[html.Button('Add first weather predition')]),
                dt.DataTable(id="w1dt", rows=[{'Time':[], 'Value':[]}]) if active_device.weatherPredictions1 is None else dt.DataTable(id="w1dt", rows=active_device.weatherPredictions1.to_dict('records')),
                dcc.Upload(id="weather2", children=[html.Button('Add second weather predition')]),
                dt.DataTable(id="w2dt", rows=[{'Time':[], 'Value':[]}]) if active_device.weatherPredictions2 is None else dt.DataTable(id="w2dt", rows=active_device.weatherPredictions2.to_dict('records')),
                dcc.Upload(id="weather3", children=[html.Button('Add third weather predition')]),
                dt.DataTable(id="w3dt", rows=[{'Time':[], 'Value':[]}]) if active_device.weatherPredictions3 is None else dt.DataTable(id="w3dt", rows=active_device.weatherPredictions3.to_dict('records')),
                dcc.Upload(id="weather4", children=[html.Button('Add fourth weather predition')]),
                dt.DataTable(id="w4dt", rows=[{'Time':[], 'Value':[]}]) if active_device.weatherPredictions4 is None else dt.DataTable(id="w4dt", rows=active_device.weatherPredictions4.to_dict('records')),
            ])
        return html.Div(output)

def parse_csv(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string) #decoded is now bytes
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

@app.callback(Output('loadOrPredictionTable', 'rows'), [Input('LoadPredictionUpload', 'contents')], [State('LoadPredictionUpload', 'filename')])
def update_table(contents, filename):
    df = parse_csv(contents, filename)
    return df.to_dict('records')

@app.callback(Output('w1dt', 'rows'), [Input('weather1', 'contents')], [State('weather1', 'filename')])
def update_w1(contents, filename):
    df = parse_csv(contents, filename)
    return df.to_dict('records')

@app.callback(Output('w2dt', 'rows'), [Input('weather2', 'contents')], [State('weather2', 'filename')])
def update_w2(contents, filename):
    df = parse_csv(contents, filename)
    return df.to_dict('records')

@app.callback(Output('w3dt', 'rows'), [Input('weather3', 'contents')], [State('weather3', 'filename')])
def update_w3(contents, filename):
    df = parse_csv(contents, filename)
    return df.to_dict('records')

@app.callback(Output('w4dt', 'rows'), [Input('weather4', 'contents')], [State('weather4', 'filename')])
def update_w4(contents, filename):
    df = parse_csv(contents, filename)
    return df.to_dict('records')

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
def close_jobModal_callback(n,n2):
    return 0

''' Functions for developing mode'''

@app.callback(Output('nInfo', 'children'), [Input('neighbourhood_div', 'children')])
def showNid(children):
    global main_neighbourhood
    global active_house
    return html.Div([
        html.Div('nabolag: ' + str(len(main_neighbourhood.houses)),
                 id="main_neighbourhood-info"),
        html.Div('hus: ' + str(type(active_house)), id="active_house-info"),
        html.Div('device: ' + str(active_device), id="active_device-info"),
        html.Div('device: ' + str(active_device), id="deviceTwo"),
    ])

# set active house.

@app.callback(Output('active_house-info', 'children'), [Input('neighbourhoodTabs', 'value')])
def setActiveHouse(value):
    global active_house
    global main_neighbourhood
    if value is not None:
        active_house = main_neighbourhood.findHouseById(int(value))
    return html.Div(str(type(active_house)))


@app.callback(Output('active_device-info', 'children'), [Input('user-device-dropdown', 'value')])
def setActiveDevice(value):
    global active_house
    global active_device
    if value is not None:
        active_device = active_house.findDeviceById(int(value))
    return html.Div(str(active_device))

@app.callback(Output('deviceTwo', 'children'), [Input('jobs_device_dropdown', 'value')])
def setADevice(value):
    global active_house
    global active_device
    if value is not None:
        active_device = active_house.findDeviceById(int(value))
    return html.Div(str(active_device))


# Change tab on delete. TODO:reset n and send signal instead of timestamp on adding house
@app.callback(Output('neighbourhoodTabs', 'value'), [Input('btnDeleteHouse', 'n_clicks_timestamp')])
def tabChangeOnDelete(a, b):
    if int(a) > int(b):
        return str(main_neighbourhood.houses[0].id)


@app.callback(Output('job_modal', 'style'), [Input('btnAddJob', 'n_clicks')])
def displayJobModal(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}

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
    if n > 0:
        global active_house
        global active_device
        if (estDate, estTime, lstDate, lstTime) is not None:
            est = createEpochTime(estDate, estTime)
            lst = createEpochTime(lstDate, lstTime)
            timeAdded = int(time.time())
        if active_device.type == 'consumer':
            job = str(timeAdded)+';'+ str(est) + ';' + str(lst)+ ';[' + str(active_house.id)+'];[' + str(active_device.id)+'];'+str(active_device.id) +'.csv'
            active_device.events.append(job)
 
def createEpochTime(date, time):
    d = date.split('-')
    t = time.split(':')
    dateTime = datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1])).timestamp()
    return int(dateTime)

#autogenerate sunny weatherprediciton

@app.callback(Output('save_hidden', 'children'), [Input('btnSaveNeighbourhood', 'n_clicks'), Input('neighbourhoodName', 'value')])
def save_neighbourhood(n, value):
    global main_neighbourhood
    global addedLoads
    if value and (n and n > 0):
        filepath=ROOT_DIR+"/input/"+value
        os.makedirs(filepath)
        os.makedirs(filepath+"/loads")
        os.makedirs(filepath+"/predictions")
        producerEvents = []
        #make dir loads, prediction, consumerevent.csv, produserevent.csv
        for house in main_neighbourhood.houses:
            for device in house.users[0].devices: #only one user in each house
                if device.type == "producer":
                    if device.weatherPredictions1 is not None:
                        device.weatherPredictions1.to_csv(filepath+"/predictions/"+str(house.id)+"_"+str(device.id)+"_1.csv", sep=" ", index=False, header=False)
                        producerEvents.append(str(device.weatherPredictions1['Time'].iloc[0] + ';pv_producer[' + str(house.id) +']:['+str(device.id)+'];'+str(house.id)+"_"+str(device.id)+'_1.csv'))
                    if device.weatherPredictions2 is not None:
                        device.weatherPredictions2.to_csv(filepath+"/predictions/"+str(house.id)+"_"+str(device.id)+"_2.csv", sep=" ", index=False, header=False)
                        producerEvents.append(str(device.weatherPredictions2['Time'].iloc[0] + ';pv_producer[' + str(house.id) +']:['+str(device.id)+'];'+str(house.id)+"_"+str(device.id)+'_2.csv'))
                    if device.weatherPredictions3 is not None:
                        device.weatherPredictions3.to_csv(filepath+"/predictions/"+str(house.id)+"_"+str(device.id)+"_3.csv", sep=" ", index=False, header=False)
                        producerEvents.append(str(device.weatherPredictions3['Time'].iloc[0] + ';pv_producer[' + str(house.id) +']:['+str(device.id)+'];'+str(house.id)+"_"+str(device.id)+'_3.csv'))
                    if device.weatherPredictions4 is not None:
                        device.weatherPredictions4.to_csv(filepath+"/predictions/"+str(house.id)+"_"+str(device.id)+"_4.csv", sep=" ", index=False, header=False)
                        producerEvents.append(str(device.weatherPredictions4['Time'].iloc[0] + ';pv_producer[' + str(house.id) +']:['+str(device.id)+'];'+str(house.id)+"_"+str(device.id)+'_4.csv'))
                elif device.type == "consumer":
                    if device.loadProfile is not None:
                        device.loadProfile.to_csv(filepath+"/loads/"+str(device.id)+".csv", sep=" ", index=False, header=False)
                    with open(filepath+'/consumer_event.csv', 'a+') as consumerJobscsv:
                        wr = csv.writer(consumerJobscsv, delimiter='\n')
                        wr.writerow(device.events)
        with open(filepath+'/consumer_event.csv', 'a+') as jobscsv:
            wr = csv.writer(jobscsv, delimiter='\n')
            wr.writerow(addedLoads)

        with open(filepath+'/producer_event.csv', 'a+') as producerJobscsv:
            wr = csv.writer(producerJobscsv, delimiter='\n')
            wr.writerow(producerEvents)

        #pickle neighbourhood object and save it locally?
        
                    
        

