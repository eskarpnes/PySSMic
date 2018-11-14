import base64
import datetime
import io
import xml.etree.ElementTree as ET
import pandas as pd
import time
import csv
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import datetime
import sys
import os
import pickle
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.neighbourhood import Neighbourhood, House, Device, Event, User
from app import app
from definitions import ROOT_DIR

# Global variables. This makes the app works in a localhost environment only
main_neighbourhood = None
active_house = None
active_device = None


# Resets all global variables
@app.callback(Output("reset", "children"), [Input("init_choices", "children")])
def reset_globals(c):
    global main_neighbourhood
    global active_house
    global active_device
    main_neighbourhood = None
    active_house = None
    active_device = None

"""--- START Functions to render a view for the Neighbourhood ---"""
def create_house_tab(house):
    return (dcc.Tab(label="House Id: " + str(house.id), value=str(house.id)))

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
        

            if device.weatherPredictions1 is not None and len(device.weatherPredictions1['Time'].iloc[0]) > 0:
                content.append(
                html.Tr([
                    html.Td(device.id),
                    html.Td(device.name),
                    html.Td(device.template),
                    html.Td(device.type),
                    html.Td(unixToDate(int(device.weatherPredictions1['Time'].iloc[0])))
            ])
            )
            else:
                content.append(
                html.Tr([
                    html.Td(device.id),
                    html.Td(device.name),
                    html.Td(device.template),
                    html.Td(device.type)]))
    return content

def create_jobs_list(house):
    jobs=[]
    for device in house.users[0].devices:
        for event in device.events:
            jobs.append(
                html.Tr([
                    html.Td(device.name),
                    html.Td(unixToString(event.timestamp)),
                    html.Td(unixToString(event.est)),
                    html.Td(unixToString(event.lst))]))
    return jobs


def display_house(house):
    if len(house.users[0].devices) < 1:
        return html.Div(className="house_content_empty", children=["This house is empty"])
    return html.Div([
                    html.Table(className="house_content_table", children=[
                        html.Tr([ #TableRow with tableheaders
                            html.Th("Device ID"),
                            html.Th("Name"),
                            html.Th("Template"),
                            html.Th("Type"),
                            html.Th("PV Date")
                        ])] +
                        create_house_view(house)
                    ),
                     html.H5(className="tabcontent_header", children=["Jobs in house:"]),
                     html.Table(className="house_content_table", children=[
                         html.Tr([ #TableRow with tableheaders
                             html.Th("Device"),
                             html.Th("Time"),
                             html.Th("Est"),
                             html.Th("Lst")])] + 
                         create_jobs_list(house))])


@app.callback(Output("tabs", "children"),
              [Input("neighbourhood_div", "children")])
def neighbourhood_tab_view(dictionary):
    global main_neighbourhood
    if main_neighbourhood is not None:
        tabs = create_house_tabs(main_neighbourhood)
        return html.Div(children=[
            dcc.Tabs(id="neighbourhood_tabs",
                     children=tabs),
            html.Div(id="tabs_content")])


@app.callback(Output("tabs_content", "children"),
              [Input("neighbourhood_tabs", "value"),
              Input("save_job", "n_clicks"),
              Input("jobs_xml", "contents")])
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
        house = main_neighbourhood.find_house_by_id(tabId)
        if house is not None:
            dis = display_house(house)
            return html.Div([dis])


"""--- END Functions to render a view for the Neighbourhood ---"""
# Modal which runs all the time, but are shown when user clicks on "Configure house" button
def config_house_modal():
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
                                    id="house_modal_close",
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
                        dcc.Tabs(id="config_house_tabs", value="add_new_consumer", children=[
                            dcc.Tab(label="Configure a device",
                                    value="config_house_device"),
                            dcc.Tab(label="Add new consumer",
                                    value="add_new_consumer"),
                            dcc.Tab(label="Add new producer",
                                    value="add_new_producer")
                        ]),
                        # form
                        html.Div(id="configHouse-content", children=[
                            dcc.Input(id="new_device_id"),
                            dcc.Input(id="new_device_name"),
                            dcc.Input(id="new_device_template"),
                            dcc.Dropdown(id="new_device_type"),
                            dcc.Upload(id="weather1"),
                            dt.DataTable(id="w1dt", rows=[{"Time": [], "Value": []}]),
                            dcc.Upload(id="weather2"),
                            dt.DataTable(id="w2dt", rows=[{"Time": [], "Value": []}]),
                            dcc.Upload(id="weather3"),
                            dt.DataTable(id="w3dt", rows=[{"Time": [], "Value": []}]),
                            dcc.Upload(id="weather4"),
                            dt.DataTable(id="w4dt", rows=[{"Time": [], "Value": []}]),
                            dcc.Upload(id="load_prediction_upload"),
                            dt.DataTable(id="load_prediction_table", rows=[{"Time": [], "Value": []}])
                        ]),
                        html.Button(
                            "Save",
                            id="save_consumer",
                            n_clicks_timestamp="0",
                        ),
                        html.Button(
                            "Save",
                            id="save_producer",
                            n_clicks_timestamp="0",
                        ),
                        html.Button("Delete device", id="btn_delete_device", n_clicks_timestamp="0")
                    ],
                    className="modal_content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="house_modal",
        style={"display": "none"},
    )


# Modal which runs all the time, but are shown when user clicks on "Add job" button
def add_job_modal():
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

                        html.Div(id="add_jobs_content", children=[
                            dcc.Dropdown(id="jobs_device_dropdown"),
                            dcc.DatePickerSingle(id="est_date_picker"),
                            dcc.Input(id="est_time_picker"),
                            dcc.DatePickerSingle(id="lst_date_picker"),
                            dcc.Input(id="lst_time_picker")
                        ]),
                        html.Button(
                            "Save",
                            id="save_job",
                            n_clicks_timestamp="0",
                            className="button button--primary add"
                        ),
                        html.Button("Delete")
                    ],
                    className="modal_content",
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
    html.Div(id="save_hidden", style={"display": "none"}),
    html.Div(id="reset", style={"display": "none"}),
    html.Div(id="save_jobs", style={"display": "none"}),
    html.Div(id="save_jobs_fromxml", style={"display": "none"}),
    html.Div(id="consumer_div", style={"display": "none"}),
    html.Div(id="producer_div", style={"display": "none"}),
    html.Div(id="n_info", children=[
        html.Div("nabolag: " + str(main_neighbourhood),id="main_neighbourhood_info"),
        html.Div("hus: " + str(type(active_house)), id="active_house-info"),
        html.Div("device: " + str(active_device), id="active_device_info"),
        html.Div("device:", id="deviceTwo")], style={"display": "none"}),
    html.H4("Create a new neighbourhood"),
    html.Div(id="init_choices", children=[
        html.Button("Create new from scratch", id="btn_new_neighbourhood", n_clicks_timestamp="0"),
        dcc.Upload(id="upload_data", children=[html.Button("Create new from XML")]),
        dcc.Upload(id="load_neighbourhood_pickle", children=[html.Button("Load Pickle")])
    ]),
    html.Div(id="new_house_input", children=[
        html.Button("Add house", id="btn_add_house", n_clicks_timestamp="0"),
        html.Button("Delete house", id="btn_delete_house",
                    n_clicks_timestamp="0"),
        html.Button("Add or config device", id="btn_config_house",
                    n_clicks_timestamp="0"),
        html.Button("Add job", id="btn_add_job", n_clicks_timestamp="0"),
        dcc.Upload(id="jobs_xml", children=[html.Button("Add jobs from XML")])],
             style={"display": "none"}),
    html.Div(id="neighbourhood_info"),
    html.Div(id="tabs", children=[
        dcc.Tabs(id="neighbourhood_tabs",
                     children=[dcc.Tab()]),
            html.Div(id="tabs_content")
    ]),
    html.Div(id="save_neighbourhood", children=[
        dcc.Input(id="neighbourhood_name", placeholder="neighbourhood_name"),
        html.Button("Save Neighbourhood", id="btn_save_neighbourhood"),
        html.Div(id="save_neighbourhood_feedback", children=["Neighbourhood added to your input folder!"], style={"display":"none"}),
    ],
             style={"display": "none"}),

    config_house_modal(),
    add_job_modal()
], className="create_esn_div")

"""--- START functions to parse xml and csv files for user input and create python objects/list of them ---"""
def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(",")
        if "xml" in content_type:
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
            h = main_neighbourhood.find_house_by_id(int(house.get("id")))
            if h is not None:
                for user in house:
                    for device in user:
                        d_id = device.find("id").text
                        d = h.find_device_by_id(int(d_id))
                        if d is not None:
                            timestamp =device.find("creation_time").text
                            est=device.find("est").text
                            lst=device.find("lst").text
                            d.events.append(Event(int(timestamp), int(est), int(lst)))


def parse_csv(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)  # decoded is now bytes
        string = io.StringIO(decoded.decode("utf-8"))
        timestamps = []
        values = []
        for line in string:
            if line is not "":
                split_line = line.split(" ")
                timestamps.append(split_line[0])
                values.append(split_line[1].rstrip())
        output = [("Time", timestamps),
                  ("Value", values)]
        df = pd.DataFrame.from_dict(dict(output))
        return df


"""--- END functions to parse xml and csv files for user input and create python objects of them ---"""


@app.callback(Output("save_jobs_fromxml", "children"), [Input("jobs_xml", "contents")])
def create_job_list(contents):
    root = parse_contents(contents)
    create_loads_list(root)

# Saves neighbourhood in hidden div on main page, so the output div can update on multiple other events
# Function to store and update main neighbourhood div / Controller


@app.callback(Output("consumer_div", "children"),
              [Input("save_consumer", "n_clicks_timestamp")],
              [
                  State("new_device_id", "value"),
                  State("new_device_name", "value"),
                  State("new_device_template", "value"),
                  State("new_device_type", "value"),
                  State("load_prediction_table", "rows")
              ])
def add_consumer(n, dId, dName, dTemp, dType, rows):
    global active_house
    global active_device
    if (dId or dName or dTemp or dType) is not None:
        dev = Device(dId, dName, dTemp, dType)
        if rows and len(rows[0]['Time']) > 0:
            dev.load_profile = pd.DataFrame(rows)
        if active_device is None:
            active_house.users[0].devices.append(dev)
        elif active_device is not None:
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
    return html.Div("hello")


@app.callback(Output("producer_div", "children"),
              [Input("save_producer", "n_clicks_timestamp")],
              [
                  State("new_device_id", "value"),
                  State("new_device_name", "value"),
                  State("new_device_template", "value"),
                  State("new_device_type", "value"),
                  State("w1dt", "rows"),
                  State("w2dt", "rows"),
                  State("w3dt", "rows"),
                  State("w4dt", "rows"),
              ])
def config_producer(n, dId, dName, dTemp, dType, w1, w2, w3, w4):
    global main_neighbourhood
    global active_house
    global active_device
    if (dId or dName or dTemp or dType) is not None:
        dev = Device(dId, dName, dTemp, dType)
        dev.weather_prediction1 = pd.DataFrame(w1) if w1 is not None else None
        dev.weather_prediction2 = pd.DataFrame(w2) if w2 is not None else None
        dev.weather_prediction3 = pd.DataFrame(w3) if w3 is not None else None
        dev.weather_prediction4 = pd.DataFrame(w4) if w4 is not None else None
        if active_device is None:
            active_house.users[0].devices.append(dev)
        elif active_device is not None:
            main_neighbourhood.find_house_by_id(active_house.id)
            active_house.users[0].devices.remove(active_device)
            active_house.users[0].devices.append(dev)
        return html.Div(str(dev.weather_prediction1))
    return html.Div("hello")


"""
This function does most of the logic when adding and removing houses,devices, jobs to the neighbourhood
Updates the main_neighbourhood
"""
def nei_from_pickle(filename):
    filepath = ROOT_DIR+"/neighbourhoods/"+filename
    with open(filepath, "rb") as f:
        nei = pickle.load(f)
    return nei

@app.callback(Output("neighbourhood_div", "children"),
              [
                  Input("upload_data", "contents"),
                  Input("load_neighbourhood_pickle", "filename"),
                  Input("btn_new_neighbourhood", "n_clicks_timestamp"),
                  Input("btn_add_house", "n_clicks_timestamp"),
                  Input("btn_delete_house", "n_clicks_timestamp"),
                  Input("save_consumer", "n_clicks_timestamp"),
                  Input("save_producer", "n_clicks_timestamp"),
                  Input("btn_delete_device", "n_clicks_timestamp")
              ])
def configure_neighbourhood(contents, pickle, btn_new_nei, btn_add_house, btn_remove_house, btn_save_consumer, btn_save_producer,
                            btn_delete_device):
    global main_neighbourhood
    global active_house
    global active_device
    # finds the button which was pressed last
    btnclicks = [btn_new_nei, btn_add_house, btn_remove_house, btn_save_consumer, btn_save_producer, btn_delete_device]
    btnclicks.sort(key=int)
    # Actions for the different buttons
    if btn_new_nei != "0" and btn_new_nei == btnclicks[-1]:
        newHouse = House(1)
        newHouse.users.append(User(1))
        main_neighbourhood = Neighbourhood(1)
        main_neighbourhood.houses.append(newHouse)
        active_house = main_neighbourhood.houses[0]
    elif btn_add_house != "0" and btn_add_house == btnclicks[-1]:
        i = main_neighbourhood.nextHouseId()
        newHouse = House(i)
        newHouse.users.append(User(1))
        main_neighbourhood.houses.append(newHouse)
    elif btn_remove_house != "0" and btn_remove_house == btnclicks[-1]:
        i = main_neighbourhood.houses.index(active_house)
        main_neighbourhood.houses.remove(active_house)
    elif (btn_save_consumer != "0" or btn_save_producer != "0") and (btn_save_consumer or btn_save_producer) == btnclicks[-1]:
        pass  # needed to take this functionality and move it to addDevice function. See line 336.
    elif btn_delete_device != "0" and btn_delete_device == btnclicks[-1]:
        active_house.users[0].devices.remove(active_device)
    elif main_neighbourhood is None and pickle is not None:
        main_neighbourhood = nei_from_pickle(pickle)
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


def show(n, contents, filename):
    if (n and n > 0) or contents or filename:
        return {"display": "flex"}
    return {"display":"none"}


@app.callback(Output("new_house_input", "style"),
              [Input("btn_new_neighbourhood", "n_clicks"), Input("upload_data", "contents"), Input("load_neighbourhood_pickle", "contents")])
def show_menu(n, contents, filename):
    return show(n, contents, filename)


@app.callback(Output("save_neighbourhood", "style"),
              [Input("btn_new_neighbourhood", "n_clicks"), Input("upload_data", "contents"), Input("load_neighbourhood_pickle", "contents")])
def show_save_button(n, contents, filename):
    return show(n, contents, filename)


@app.callback(Output("init_choices", "style"), [Input("tabs", "children")])
def hide_button(children):
    if children and len(children) > 1:
        return {"display": "none"}


@app.callback(Output("house_modal", "style"), [Input("btn_config_house", "n_clicks")])
def display_leads_modal_callback(n):
    if n and n > 0:
        global active_device
        active_device = None
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("btn_config_house", "n_clicks"),
    [Input("house_modal_close", "n_clicks"),
     Input("save_consumer", "n_clicks"),
     Input("save_producer", "n_clicks"),
     Input("btn_delete_device", "n_clicks")]
)
def close_modal_callback(n, n2, n3, n4):
    return 0


@app.callback(
    Output("btn_add_job", "n_clicks"),
    [Input("job_modal_close", "n_clicks"),
     Input("save_job", "n_clicks")],
)
def close_job_modal_callback(n, n2):
    return 0


@app.callback(Output("job_modal", "style"), [Input("btn_add_job", "n_clicks")])
def display_job_modal(n):
    if (n and n > 0):
        return {"display": "block"}
    return {"display": "none"}


""" --- END functions to show change the style to different divs and modals ---"""

"""--- START Callback functions to render input fields based on which type of device the user want to change---"""
@app.callback(Output("add_jobs_content", "children"), [Input("job_modal", "style")])
def render_add_job_content(style):
    global active_house
    if style == {"display": "block"}:
        return html.Div(id="add_job", children=[
            html.Div(id="add_job_content"),
            dcc.Dropdown(id="jobs_device_dropdown", placeholder="Choose device",
                         options=[{"label": device.name, "value": device.id}
                                  for user in active_house.users for device in user.devices]),
            html.H4("Earliest Start time"),
            dcc.DatePickerSingle(
                id="est_date_picker",
                initial_visible_month=datetime.datetime.now()

            ),
            html.Br(),
            dcc.Input(
                id="est_time_picker",
                type="time",
                placeholder="HH:MM"
            ),
            html.H4("Latest start time"),
            dcc.DatePickerSingle(
                id="lst_date_picker",
                initial_visible_month=datetime.datetime.now()
            ),
            html.Br(),
            dcc.Input(
                id="lst_time_picker",
                type="time",
                placeholder="HH:MM"
            )
        ]),


def create_producer_modal_form(did, name, temp, devtype, w1, w2, w3, w4):
    return html.Div(className="producer_modal_form", children=[
            html.Div(className="dev_id", children=[
                html.Div("Device ID:"),
                dcc.Input(id="new_device_id", type="number", value=did, className="modal_input_field")
            ]),
            html.Div(className="dev_name", children=[
                html.Div("Device Name:"),
                dcc.Input(id="new_device_name", type="text", placeholder="", value=name, className="modal_input_field")
            ]),
            html.Div(className="dev_temp", children=[
                html.Div("Device Template:"),
                dcc.Input(id="new_device_template", type="number", placeholder="template", value=temp, className="modal_input_field")
            ]),
            html.Div(className="dev_type", children=[
                html.Div("Device Type:"),
                dcc.Dropdown(id="new_device_type",
                         options=[{"label": "Producer", "value": "producer"}],
                         value=devtype)
            ]),
            html.Div(className="pv1", children=[
                dcc.Upload(id="weather1", className="w1Pred", children=[html.Button("Add First Prediction")]),
                dt.DataTable(id="w1dt", rows=w1)
            ]),
            html.Div(className="pv2", children=[
                dcc.Upload(id="weather2", className="w2Pred", children=[html.Button("Add Second Prediction")]),
                dt.DataTable(id="w2dt", rows=w2),
            ]),
            html.Div(className="pv3", children=[
                dcc.Upload(id="weather3", className="w3Pred", children=[html.Button("Add Third Prediction")]),
                dt.DataTable(id="w3dt", rows=w3),
            ]),
            html.Div(className="pv4", children=[
                dcc.Upload(id="weather4", className="w4Pred", children=[html.Button("Add Fourth Prediction")]),
                dt.DataTable(id="w4dt", rows=w4)
            ])
        ])


def create_consumer_modal_form(did, name, temp, dtype, load):
    return html.Div(className="consumer_modal_form", children=[
            html.Div(className="dev_id", children=[
                html.Div("Device ID:"),
                dcc.Input(id="new_device_id", type="number", value=did, className="modal_input_field")
            ]),
            html.Div(className="dev_name", children=[
                html.Div("Device Name:"),
                dcc.Input(id="new_device_name", type="text", value=name, className="modal_input_field")
            ]),
            html.Div(className="dev_temp", children=[
                html.Div("Device Template:"),
                dcc.Input(id="new_device_template", type="number", value=temp, className="modal_input_field")
            ]),
            html.Div(className="dev_type", children=[
                html.Div("Device Type:"),
                dcc.Dropdown(id="new_device_type",
                         options=[{"label": "Consumer", "value": "consumer"}],
                         value=dtype)
            ]),
            dcc.Upload(id="load_prediction_upload", className="dev_load", children=[html.Button("Add load csv file")]),
            html.Div(className="load_table", children=[
                dt.DataTable(id="load_prediction_table", rows=load)
            ])
        ])


@app.callback(Output("configHouse-content", "children"), [Input("config_house_tabs", "value")])
def show_house_config_content(value):
    global active_house
    global active_device
    empty_p = [{"Time": [], "Value": []}]
    if value == "config_house_device":
        return html.Div([
            dcc.Dropdown(id="user-device-dropdown", options=[{"label": device.name, "value": device.id}
                                                             for user in active_house.users for device in user.devices],
                         placeholder="Select device"),
            html.Div(id="device_config_form")
        ])
    elif value == "add_new_consumer":
        active_device = None
        return create_consumer_modal_form(0, "", 0, "consumer", empty_p)
    elif value == "add_new_producer":
        active_device = None
        return create_producer_modal_form(0, "", 0, "producer", empty_p, empty_p, empty_p, empty_p)


@app.callback(Output("device_config_form", "children"), [Input("active_device_info", "children")])
def render_config_form(children):
    empty_p = [{"Time": [], "Value": []}]
    if active_device is not None:
        if active_device.type== "consumer":
            l = empty_p if active_device.load_profile is None else active_device.load_profile.to_dict("records")
            return create_consumer_modal_form(active_device.id, active_device.name, active_device.template, active_device.type, l)
        
        elif active_device.type == "producer":
            pv1 = empty_p if active_device.weather_prediction1 is None else active_device.weather_prediction1.to_dict("records")
            pv2 = empty_p if active_device.weather_prediction2 is None else active_device.weather_prediction2.to_dict("records")
            pv3 = empty_p if active_device.weather_prediction3 is None else active_device.weather_prediction3.to_dict("records")
            pv4 = empty_p if active_device.weather_prediction4 is None else active_device.weather_prediction4.to_dict("records")
            return create_producer_modal_form(active_device.id, active_device.name, active_device.template, active_device.type, pv1, pv2, pv3, pv4)


@app.callback(Output("save_consumer", "style"), [Input("config_house_tabs", "value"), Input("active_device_info", "children")])
def toggle_save_button(v1, c):
    if v1 == "config_house_device":
        if active_device is not None and active_device.type== "consumer":
            return {"display":"inline-block"}
    if v1 == "add_new_consumer":
        return {"display":"inline-block"}
    else:
        return {"display":"none"}


@app.callback(Output("save_producer", "style"), [Input("config_house_tabs", "value"), Input("active_device_info", "children")])
def toggle_save_prod_button(v1, c):
    if v1 == "config_house_device":
        if active_device is not None and active_device.type== "producer":
            return {"display":"inline-block"}
    if v1 == "add_new_producer":
        return {"display": "inline-block"}
    else:
        return {"display": "none"}


"""--- END Callback functions to render input fields based on which type of device the user want to change---"""


"""---START functions to update dash DataTable based on inputs from user ---"""


@app.callback(Output("load_prediction_table", "rows"), [Input("load_prediction_upload", "contents")],
              [State("load_prediction_upload", "filename")])
def update_table(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict("records")
    elif active_device and active_device.load_profile is not None:
        if len(active_device.load_profile["Time"].iloc[0]) > 0:
            return active_device.load_profile.to_dict("records")
    else:
        return [{"Time": [], "Value": []}]


@app.callback(Output("w1dt", "rows"), [Input("weather1", "contents")], [State("weather1", "filename")])
def update_w1(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict("records")
    elif active_device and active_device.weather_prediction1 is not None:
        if len(active_device.weather_prediction1["Time"].iloc[0]) > 0:
            return active_device.weather_prediction1.to_dict("records")
    else:
        return [{"Time": [], "Value": []}]


@app.callback(Output("w2dt", "rows"), [Input("weather2", "contents")], [State("weather2", "filename")])
def update_w2(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict("records")
    elif active_device and active_device.weather_prediction2 is not None:
        if len(active_device.weather_prediction2["Time"].iloc[0]) > 0:
            return active_device.weather_prediction2.to_dict("records")
    else:
        return [{"Time": [], "Value": []}]


@app.callback(Output("w3dt", "rows"), [Input("weather3", "contents")], [State("weather3", "filename")])
def update_w3(contents, filename):
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict("records")
    elif active_device and active_device.weather_prediction3 is not None:
        if len(active_device.weather_prediction3["Time"].iloc[0]) > 0:
            return active_device.weather_prediction3.to_dict("records")
    else:
        return [{"Time": [], "Value": []}]


@app.callback(Output("w4dt", "rows"), [Input("weather4", "contents")], [State("weather4", "filename")])
def update_w4(contents, filename):
    global active_device
    if contents is not None:
        df = parse_csv(contents, filename)
        return df.to_dict("records")
    elif active_device and active_device.weather_prediction4 is not None:
        if len(active_device.weather_prediction4["Time"].iloc[0]) > 0:
            return active_device.weather_prediction4.to_dict("records")
    else:
        return [{"Time": [], "Value": []}]


"""---END functions to update dash DataTable based on inputs from user ---"""


"""--- Start Functions to set the global variables when interacting with the GUI---"""


@app.callback(Output("active_house-info", "children"), [Input("neighbourhood_tabs", "value")])
def set_active_house(value):
    global active_house
    global main_neighbourhood
    if value is not None:
        active_house = main_neighbourhood.find_house_by_id(int(value))
    return html.Div(str(type(active_house)))


def set_active_device(value):
    global active_house
    global active_device
    if value is not None:
        active_device = active_house.find_device_by_id(int(value))
    return html.Div(str(type(active_device)))


@app.callback(Output("active_device_info", "children"), [Input("user-device-dropdown", "value")])
def setActiveDevice(value):
    return set_active_device(value)


@app.callback(Output("deviceTwo", "children"), [Input("jobs_device_dropdown", "value")])
def setADevice(value):
    return set_active_device(value)


"""--- END Functions to set the global variables when interacting with the GUI---"""


# Function to add Jobs to specific devices
@app.callback(Output("save_jobs", "children"),
              [Input("save_job", "n_clicks")],
              [
                  State("est_date_picker", "date"),
                  State("est_time_picker", "value"),
                  State("lst_date_picker", "date"),
                  State("lst_time_picker", "value")
              ])
def save_jobs(n, est_date, est_time, lst_date, lst_time):
    if n and n > 0:
        global active_house
        global active_device
        if (est_date, est_time, lst_date, lst_time) is not None:
            est = createEpochTime(est_date, est_time)
            lst = createEpochTime(lst_date, lst_time)
            timeAdded = est
        if active_device.type == "consumer":
            active_device.events.append(Event(timeAdded, est, lst))


def createEpochTime(date, time):
    d = date.split("-")
    t = time.split(":")
    dateTime = datetime.datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1])).timestamp()
    return int(dateTime)


def create_pv_csv_files(filepath, prediction, house, device, n):
    prediction.to_csv(filepath + "/predictions/" + str(house.id) + "_" + str(device.id) + "_"+str(n)+".csv", sep=" ", index=False, header=False)
    return "{};pv_producer[{}]:[{}];{}_{}_{}.csv".format(prediction["Time"].iloc[0], house.id, device.id, house.id, device.id, n)


def create_consumer_csv_files(event, house, device):
    return "{};{};{};[{}]:[{}]:[{}];{}.csv".format(str(event.timestamp), str(event.est), str(event.lst), str(house.id), str(device.id), str(device.id), str(device.id)) #Maybe include templatenumber?


def unixToString(time):
    return datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')


def makeDirs(n, value):
    filepath = ROOT_DIR + "/input/" + value
    if os.path.isdir(filepath):
        value+="_1"
        makeDirs(n, value)
    os.makedirs(filepath)
    os.makedirs(filepath + "/loads")
    os.makedirs(filepath + "/predictions")
    return filepath

def unixToDate(time):
    return datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d')



#Function to create files for simulation.
@app.callback(Output("save_hidden", "children"),
              [Input("btn_save_neighbourhood", "n_clicks")],
              [State("neighbourhood_name", "value")])
def save_neighbourhood(n, value):
    global main_neighbourhood
    if n and n > 0:
        if value is None:
            value = "no_name"
        filepath = makeDirs(n, value)
        producer_events = []
        consumer_events =[]
        # make dir loads, prediction, consumerevent.csv, produserevent.csv
        for house in main_neighbourhood.houses:
            for device in house.users[0].devices:  # only one user in each house
                if device.type == "producer":
                    if device.weather_prediction1 is not None and len(device.weather_prediction1["Time"].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weather_prediction1, house, device, 1))
                    if device.weather_prediction2 is not None and len(device.weather_prediction2["Time"].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weather_prediction2, house, device, 2))
                    if device.weather_prediction3 is not None and len(device.weather_prediction3["Time"].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weather_prediction3, house, device, 3))
                    if device.weather_prediction4 is not None and len(device.weather_prediction4["Time"].iloc[0]) > 0:
                        producer_events.append(create_pv_csv_files(filepath, device.weather_prediction4, house, device, 4))
                elif device.type == "consumer":
                    if device.load_profile is not None and len(device.load_profile["Time"].iloc[0]) > 0:
                        device.load_profile.to_csv(filepath + "/loads/" + str(device.id) + ".csv", sep=" ", index=False,
                                                  header=False)
                    for event in device.events:
                        consumer_events.append(create_consumer_csv_files(event, house, device))
        with open(filepath + "/consumer_event.csv", "a+") as consumerJobscsv:
            wr = csv.writer(consumerJobscsv, delimiter="\n")
            wr.writerow(consumer_events)
        with open(filepath + "/producer_event.csv", "a+") as producerJobscsv:
            wr = csv.writer(producerJobscsv, delimiter="\n")
            wr.writerow(producer_events)

        fpath = ROOT_DIR+"/neighbourhoods/"+value+".pkl"
        with open(fpath, "wb") as f:
            pickle.dump(main_neighbourhood, f)


@app.callback(Output("save_neighbourhood_feedback", "style"), [Input("btn_save_neighbourhood", "n_clicks")])
def give_save_feedback(n):
    if n and n>0:
        return {"display": "block"}
    return {"display": "none"}
