
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash import Dash

app = Dash(__name__)

# Define the app layout
edaLayout = app.layout = html.Div([
    html.H1('Hello World!')
    ])
