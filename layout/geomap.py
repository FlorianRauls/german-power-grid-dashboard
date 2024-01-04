import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash import Dash, callback, State
import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from .template import my_ibcs_template, titles_styles
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import json

# open geojson file
path = os.path.join('data', 'V20210507', 'europe.geojson')
with open(path) as f:
    geojson = json.load(f)
    
    
# load Photovolatic data from geojson file
path = os.path.join('data', 'V20210507', 'Photovoltaic_Field_Systems_V20210507.geojson')
with open(path) as f:
    json_photo = json.load(f)


# lon / lat of the center of Germany
center_lon = 11.5
center_lat = 51.5

fig = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = [center_lon], lat = [center_lat],
    marker = {'size': 5, 'color': ["red"]}))

fig.update_layout(
    mapbox = {
        'style': "white-bg",
        'center': { 'lon': center_lon, 'lat': center_lat},
        'zoom': 4, 'layers': [{
            'source': geojson,
            'type':'fill', 'below':'traces','color': 'grey', 'opacity' : 0.2}],
    },
    margin = {'l':0, 'r':0, 'b':0, 't':0})

# edit the layout
fig.update_layout(
    title='',
    template=my_ibcs_template,
    margin=dict(l=0, r=0, t=0, b=0),
    autosize=True,
    height=800,
)

geomap_layout = html.Div(
    children=[
        dcc.Graph(
            id='geomap',
            figure=fig,
            style={"height": "100%"}
        )
    ],
    style={"height": "100%"}
)

