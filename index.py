import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app
from apps import create_sim, create_esn, main, base
from backend.neighbourhood import Neighbourhood

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    # needed to make it work on create_esn
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return base.header, main.layout, base.footer
    elif pathname == '/apps/create_sim':
        return base.header, create_sim.layout, base.footer
    elif pathname == '/apps/create_esn':
        return base.header, create_esn.layout, base.footer
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
