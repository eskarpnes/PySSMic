import base64
import datetime
import io

import xml.etree.ElementTree as ET

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd

add_esn = dash.Dash(__name__)

add_esn.layout = html.Div([
    html.H2("Create a new neighbourhood"),

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
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])


def parse_contents(contents, filename, date):

    countries = []
    tree = ET.parse(filename)
    root = tree.getroot()
    for country in root.findall('country'):
        name = country.get('name')
        rank = country.find('rank').text
        year = country.find('year').text
        neighbors = []
        for neighbor in country.iter('neighbor'):
            neighbors.append(neighbor.attrib)

        countries.append([name, rank, year, neighbors])

    return html.Div([
        html.H5(filename),

    ])


@add_esn.callback(Output('output-data-upload', 'children'),
                  [Input('upload-data', 'contents')],
                  [State('upload-data', 'filename'),
                   State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    add_esn.run_server(debug=True)
