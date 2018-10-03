import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from src.frontend.app import app
from src.frontend.apps import create_sim, main


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return main.layout
    elif pathname == '/apps/create_sim':
         return create_sim.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)