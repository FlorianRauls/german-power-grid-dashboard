
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash import Dash
import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from .template import my_ibcs_template, titles_styles


path = os.path.join('data', 'cleaned_data.sqlite')
conn = sqlite3.connect(path)

def load_and_aggregate_data():
    # Query to fetch data from the database
    query = """
    SELECT 
        year, 
        month, 
        day,
        DE_solar_generation_actual,
        DE_wind_generation_actual,
        DE_load_actual_entsoe_transparency,
        DE_load_forecast_entsoe_transparency
    FROM 
        cleaned_data;
    """
    
    df = pd.read_sql(query, conn)

    # Convert year, month, day to a datetime object
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # Set 'date' as the index
    df.set_index('date', inplace=True)

    # Resample and aggregate by month
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    monthly_data = df[numeric_columns].resample('M').sum()

    # Reset index and extract month and year from date
    monthly_data.reset_index(inplace=True)
    monthly_data['month'] = monthly_data['date'].dt.month
    monthly_data['year'] = monthly_data['date'].dt.year
    monthly_data.drop(columns=['date'], inplace=True) 
    

    # Group by month and year and apply an aggregation function
    monthly_data = monthly_data.groupby(['year', 'month']).sum().reset_index()
    
    # recreate data column
    monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(DAY=1))
    
    # create feature for total actual generation
    monthly_data['total_actual_generation'] = monthly_data['DE_solar_generation_actual'] + monthly_data['DE_wind_generation_actual']
    
    # create feature for difference between actual and forecasted load
    monthly_data['load_diff'] =  monthly_data['DE_load_actual_entsoe_transparency'] - monthly_data['DE_load_forecast_entsoe_transparency']
    
    # remove all rows before february 2015
    monthly_data = monthly_data[monthly_data['date'] >= '2015-01-01']
    
    
    return monthly_data


# Load and aggregate data
monthly_data = load_and_aggregate_data()

# TODO: Put value over points of interest (start, end, min, max) in 10MMWh


# Create bar chart trace
trace1 = go.Bar(
    x=monthly_data['date'],
    y=monthly_data['load_diff'],
    name='Load Difference'
)


# Create layout
layout = go.Layout(
    title='Δ(AC-FC) Load',
    template=my_ibcs_template,
    yaxis=dict(
        tickformat=',.0f',
        tickmode='array',
    ),
)

# Create figure and add tracces with y-axis ticks coming every 20% of the range
fig = go.Figure(data=[trace1], layout=layout)

# find points of interest in the data: start, end, min, max
start = monthly_data['load_diff'].iloc[0] 
end = monthly_data['load_diff'].iloc[-1] 
minD = monthly_data['load_diff'].min() 
maxD = monthly_data['load_diff'].max() 

# add annotations to the figure at the points of interest
distance = 1000000
fig.add_annotation(x=monthly_data['date'].iloc[0], y=start + distance,
            text="{:.0f}".format(start/1000)+'GWh',
            showarrow=False)
fig.add_annotation(x=monthly_data['date'].iloc[-1], y=end + distance,
            text="{:.0f}".format(end/1000)+'GWh',
            showarrow=False)

fig.add_annotation(x=monthly_data['date'].iloc[monthly_data['load_diff'].idxmin()], y=minD - distance,
            text="{:.0f}".format(minD/1000)+'GWh',
            showarrow=False)

fig.add_annotation(x=monthly_data['date'].iloc[monthly_data['load_diff'].idxmax()], y=maxD + distance,
            text="{:.0f}".format(maxD/1000)+'GWh',
            showarrow=False)



edaLayout = html.Div(children=[
                        html.Div(children=[
                            dcc.Graph(id='load-diff', figure=fig)
                            ], style={'align' : 'left', 'width': '50%'}),
                            ]
    )

