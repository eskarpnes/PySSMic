import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd


from app import app


def get_energy_df():
    return pd.DataFrame({'c1': [384, 827], 'c2': [848, 874]})


def energy_use(df):
    df_sum = df.sum(axis=1)
    n = 100/(df_sum[0]+df_sum[1])
    return (
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Pie(
                        values=[df_sum[0]*n, df_sum[1]*n],
                        labels=["Local", "Not local"]
                    )
                ]
            )
        )
    )


def get_contracts():
    return {"Contract ID": [1], "Contract signed (time)": [12.32], "Start of contract (time)": [14.55], "Consumer": ["c1"], "Producer": ["p1"]}


layout = html.Div([
    html.Div(
        html.H2("Energy use")
    ),
    html.Div(
        energy_use(get_energy_df())
    ),
    html.Div(
        html.H2("Contracts")
    ),
    html.Div(
        dt.DataTable(
            rows=[get_contracts()],
            columns=["Contract ID", "Contract signed (time)", "Start of contract (time)", "Consumer", "Producer"],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="datatable"
        )
    )
])


