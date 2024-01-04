import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import os
import pandas as pd
import plotly.graph_objects as go
from .template import my_ibcs_template
import json

# open geojson file
path = os.path.join('data', 'V20210507', 'europe.geojson')
with open(path) as f:
    geojson = json.load(f)
    
    
# load Photovolatic data from geojson file
path = os.path.join('data', 'V20210507', 'Photovoltaic_Field_Systems_V20210507.geojson')
with open(path) as f:
    json_photo = json.load(f)
    
# load Wind data from geojson file
path = os.path.join('data', 'V20210507', 'Windenergy_Onshore_V20210507.geojson')
with open(path) as f:
    json_wind_onshore = json.load(f)

# load Wind data from geojson file
path = os.path.join('data', 'V20210507', 'Windenergy_Offshore_V20210507.geojson')
with open (path) as f:
    json_wind_offshore = json.load(f)

# load biomass data from geojson file
path = os.path.join('data', 'V20210507', 'Bioenergy_V20210507.geojson')
with open (path) as f:
    json_biomass = json.load(f)    

#load hydro data from geojson file
path = os.path.join('data', 'V20210507', 'Hydropower_V20210507.geojson')
with open (path) as f:
    json_hydro = json.load(f)


# get features from geojson files
features_photo = json_photo['features']
dict_template = {'type': '', 'lon' : '', 'lat' : '', 'name' : '', 'capacity' : ''}
features = json_photo['features']
features.extend(json_wind_onshore['features'])
features.extend(json_wind_offshore['features'])
features.extend(json_biomass['features'])
features.extend(json_hydro['features'])

# create list of dictionaries
list_photo = [{"type": feature["properties"]["RES"], "capacity": feature["properties"]["CAP"], "lon" : feature["properties"]["LON"], "lat" : feature["properties"]["LAT"]} for feature in features]


# create dataframe from list
df_photo = pd.DataFrame(list_photo, columns=['type', 'capacity', 'lon', 'lat'])


# lon / lat of the center of Germany
center_lon = 11.5
center_lat = 51.5

# symbols for different types of renewable energy
symbols = {'Windenergy': 0, 'Solarenergy': 304, 'Bioenergy': 113, 'Hydropower': 112}
# color the different kinds in black
colors = {'Windenergy': 'grey', 'Solarenergy': 'darkgoldenrod', 'Bioenergy': 'darkcyan', 'Hydropower': 'darkblue'}

# remove all rows where type is not in symbols
df_photo = df_photo[df_photo['type'].isin(symbols.keys())]

fig = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = df_photo["lon"], lat = df_photo["lat"],
    text = df_photo["type"],
    marker_size = df_photo["capacity"]/2250,
    marker_color = [colors[type] for type in df_photo["type"]],
    customdata=df_photo["capacity"],
    showlegend=True,
    hovertemplate = '<b>%{text}</b><br><br>' +
                    'Capacity: %{customdata} kWp<br>' +
                    '<extra></extra>',
    name = "Renewable Energy Locations",
    )
                )

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

# add legend with marker colors
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=20, color='grey'), showlegend=True, name='Windenergy'))
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=20, color='darkgoldenrod'), showlegend=True, name='Solarenergy'))
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=20, color='darkcyan'), showlegend=True, name='Bioenergy'))
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=20, color='darkblue'), showlegend=True, name='Hydropower'))

# showlegend
fig.update_layout(showlegend=True)

# restrict legend to the upper right corner
fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
))

# in the beginning show already zoomed in on Germany
fig.update_layout(mapbox_zoom=5, mapbox_center = {"lat": center_lat, "lon": center_lon})

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
 