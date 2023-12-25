# Import necessary libraries
from dash import html, dcc, dash_table, Dash
import plotly.express as px
import pandas as pd
import os
from dash.dependencies import Input, Output
from layout.eda import edaLayout

# Initialize the Dash app
app = Dash(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update page content
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/eda':
        
        return edaLayout
    else:
        return '404 - Page not found'  # You can have a default page or a 404 page



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
