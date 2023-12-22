# Import necessary libraries
import dash
from dash import html, dcc, dash_table
import plotly.express as px
import pandas as pd
import os

# Load your data
data = pd.read_csv(os.path.join('.' ,'data', 'conventional_power_plants_DE.csv'))

# Initialize the Dash app
app = dash.Dash(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Display some data in dash table for a start
table = dash_table.DataTable(
    id='data-table',
    columns=[{"name": col, "id": col} for col in data.columns],
    data=data.head().to_dict('records')
)

app.layout = html.Div(children=[
    html.H1(children='Head of the Data'),
    table
])


    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
