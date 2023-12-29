# Import necessary libraries
from dash import html, dcc, dash_table, Dash
import plotly.express as px
import pandas as pd
import os
from dash.dependencies import Input, Output
from layout.eda import edaLayout
from layout.template import titles_styles
from layout.ml import ml_layout

# Initialize the Dash app
app = Dash(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'German Energy Infrastructure'
server = app.server

app.layout = html.Div([
    html.H3(children='Florian Rauls', style=titles_styles),
    html.H3(children='Exploration of German Energy Infrastructure', style=titles_styles),
    html.H3(children='2023', style=titles_styles),
    dcc.Tabs(id="tabs-example-graph", value='data-exploration', children=[
        dcc.Tab(label='Data Exploration (2015-2020)', value='data-exploration'),
        dcc.Tab(label='Geo Map', value='geo-map'),
        dcc.Tab(label='Hourly Load Forecasting', value='ml')
    ]),
    html.Div(id='tabs-content-example-graph')
])

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'data-exploration':
        return html.Div([
                    edaLayout
        ])
    elif tab == 'geo-map':
        return html.Div([
            html.H3('Geo Map TBD'),
        ])
    elif tab == 'ml':
        return html.Div([
            ml_layout,
        ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
