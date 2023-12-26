
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
    monthly_data['load_diff'] =  monthly_data['DE_load_forecast_entsoe_transparency'] - monthly_data['DE_load_actual_entsoe_transparency']
    
    # remove all rows before february 2015
    monthly_data = monthly_data[monthly_data['date'] >= '2015-02-01']
    
    
    return monthly_data


# Load and aggregate data
monthly_data = load_and_aggregate_data()


# Create bar chart trace
trace1 = go.Bar(
    x=monthly_data['date'],
    y=monthly_data['load_diff'],
    name='Load Difference'
)


# Fit a line to the data and create line plot trace
z = np.polyfit(range(len(monthly_data)), monthly_data['load_diff'], 1)
p = np.poly1d(z)
trace2 = go.Scatter(
    x=monthly_data['date'],
    y=p(range(len(monthly_data))),
    mode='lines',
    name='Trendline'
    
)


# Create layout
layout = go.Layout(
    title='ΔForecasted - Actual Load (MWh)',
    template=my_ibcs_template,
    yaxis=dict(
        tickformat=',.0f',
        tickmode='array',
    ),
)

# Create figure and add tracces with y-axis ticks coming every 20% of the range
fig = go.Figure(data=[trace1, trace2], layout=layout)







edaLayout = html.Div(children=[
    html.H3(children='Florian Rauls', style=titles_styles),
    html.H3(children='Exploratory Data Analysis', style=titles_styles),
    html.H3(children='2015-2020', style=titles_styles),
    dcc.Graph(figure=fig)
])
