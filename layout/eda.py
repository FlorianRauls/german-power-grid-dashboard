
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
from plotly.subplots import make_subplots

path = os.path.join('data', 'cleaned_data.sqlite')
conn = sqlite3.connect(path)

def load_and_aggregate_data():
    # Query to fetch data from the database
    query = """
    SELECT 
        *
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

def gridLoadChart():
    # Create bar chart trace
    trace1 = go.Bar(
        x=monthly_data['date'],
        y=monthly_data['load_diff'],
        name='Load Difference'
    )

    # Create layout
    layout = go.Layout(
        title='Δ(AC-FC) Power Grid Load',
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
    
    fig.update_yaxes(range=[-12500000, 12500000])
    
    return fig


def renewableIncrease():
    
    # create empty figure
    fig = go.Figure()
    
    # define the layout
    fig.update_layout(
        title='ΔRenewable Production P.Y.',
        template=my_ibcs_template,
        yaxis=dict(
            tickformat=',.0f',
            tickmode='array',
        ),
    )
    
    # calculate the incrase in renewables compared to the same month in the previous year in absolute numbers
    monthly_data['renewable_increase'] = monthly_data['total_actual_generation'] - monthly_data['total_actual_generation'].shift(12)
    
    # bar chart for the increase in renewables (starting at 2016-01-01)
    fig.add_trace(go.Bar(x=monthly_data['date'], y=monthly_data['renewable_increase'], name='Renewable Increase'))
    
    # change the figure style to color positive and negative values differently
    fig.update_traces(marker_color=['green' if x > 0 else 'red' for x in monthly_data['renewable_increase']])
    
    fig.update_yaxes(range=[-12500000, 12500000])
    
    # add annotations to the figure at the points of interest
    distance = 1500000
    fig.add_annotation(x=monthly_data['date'].iloc[12], y=monthly_data['renewable_increase'].iloc[12] + distance,
                text="{:.0f}".format(monthly_data['renewable_increase'].iloc[12]/1000)+'GWh',
                showarrow=False)
    fig.add_annotation(x=monthly_data['date'].iloc[-1], y=monthly_data['renewable_increase'].iloc[-1] - distance,
                text="{:.0f}".format(monthly_data['renewable_increase'].iloc[-1]/1000)+'GWh',
                showarrow=False)
    fig.add_annotation(x=monthly_data['date'].iloc[monthly_data['renewable_increase'].idxmin()], y=monthly_data['renewable_increase'].iloc[monthly_data['renewable_increase'].idxmin()] - (4.5*distance),
                text="{:.0f}".format(monthly_data['renewable_increase'].iloc[monthly_data['renewable_increase'].idxmin()]/1000)+'GWh',
                showarrow=False)
    fig.add_annotation(x=monthly_data['date'].iloc[monthly_data['renewable_increase'].idxmax()], y=monthly_data['renewable_increase'].iloc[monthly_data['renewable_increase'].idxmax()] - distance,
                text="{:.0f}".format(monthly_data['renewable_increase'].iloc[monthly_data['renewable_increase'].idxmax()]/1000)+'GWh',
                showarrow=False)
    
    
  
    return fig


def renewable_share_by_operator(): 
    # create empty figure
    fig = go.Figure()
    
    # define the layout
    fig.update_layout(
        title='Renewable Share by Operator',
        template=my_ibcs_template,
        yaxis=dict(
            tickformat=',.0f',
            tickmode='array',
        ),
    )
    
    # calculate the share of solar and wind for each operator (Here: 50Hertz, Amprion, TenneT, TransnetBW) aggregated in sum over 2015-2020
    renewable_share = monthly_data.drop(columns=['date', 'hour', 'lag_1_hour'])
    renewable_share = renewable_share.groupby(['year']).sum()[['DE_tennet_solar_generation_actual', 'DE_tennet_wind_onshore_generation_actual', 'DE_amprion_solar_generation_actual', 'DE_amprion_wind_onshore_generation_actual', 'DE_transnetbw_solar_generation_actual', 'DE_transnetbw_wind_onshore_generation_actual', 'DE_50hertz_solar_generation_actual', 'DE_50hertz_wind_generation_actual', 'DE_tennet_load_actual_entsoe_transparency', 'DE_amprion_load_actual_entsoe_transparency', 'DE_transnetbw_load_actual_entsoe_transparency', 'DE_50hertz_load_actual_entsoe_transparency']]
    
    # calculate the share of solar and wind given the total actual generation for each operator
    renewable_share['DE_tennet_solar_share'] = renewable_share['DE_tennet_solar_generation_actual'] / renewable_share['DE_tennet_load_actual_entsoe_transparency']
    renewable_share['DE_tennet_wind_share'] = renewable_share['DE_tennet_wind_onshore_generation_actual'] / renewable_share['DE_tennet_load_actual_entsoe_transparency']
    renewable_share['DE_amprion_solar_share'] = renewable_share['DE_amprion_solar_generation_actual'] / renewable_share['DE_amprion_load_actual_entsoe_transparency']
    renewable_share['DE_amprion_wind_share'] = renewable_share['DE_amprion_wind_onshore_generation_actual'] / renewable_share['DE_amprion_load_actual_entsoe_transparency']
    renewable_share['DE_transnetbw_solar_share'] = renewable_share['DE_transnetbw_solar_generation_actual'] / renewable_share['DE_transnetbw_load_actual_entsoe_transparency']
    renewable_share['DE_transnetbw_wind_share'] = renewable_share['DE_transnetbw_wind_onshore_generation_actual'] / renewable_share['DE_transnetbw_load_actual_entsoe_transparency']
    renewable_share['DE_50hertz_solar_share'] = renewable_share['DE_50hertz_solar_generation_actual'] / renewable_share['DE_50hertz_load_actual_entsoe_transparency']
    renewable_share['DE_50hertz_wind_share'] = renewable_share['DE_50hertz_wind_generation_actual'] / renewable_share['DE_50hertz_load_actual_entsoe_transparency']
    
    # split dataframe into four dataframes for each operator
    hertz = renewable_share[['DE_50hertz_solar_share', 'DE_50hertz_wind_share']]
    amprion = renewable_share[['DE_amprion_solar_share', 'DE_amprion_wind_share']]
    tennet = renewable_share[['DE_tennet_solar_share', 'DE_tennet_wind_share']]
    transnet = renewable_share[['DE_transnetbw_solar_share', 'DE_transnetbw_wind_share']]
    
    # rename columns for each operator
    hertz.columns = ['solar_share', 'wind_share']
    amprion.columns = ['solar_share', 'wind_share']
    tennet.columns = ['solar_share', 'wind_share']
    transnet.columns = ['solar_share', 'wind_share']
    
    # add operator name as column
    hertz['operator'] = '50Hertz'
    amprion['operator'] = 'Amprion'
    tennet['operator'] = 'TenneT'
    transnet['operator'] = 'TransnetBW'
    
    # concatenate the four dataframes
    combined = pd.concat([hertz, amprion, tennet, transnet])
    combined = combined.groupby(['operator'])

    # combine solar_share and wind_share into one column but introduce a new column for the type of energy
    combined = combined.apply(lambda x: x.stack().reset_index())
    combined.columns = ['year', 'energy', 'share_in_operator_production']
    combined = combined.droplevel(1)
    
    print(combined.head())
    
    # Separate the data for solar and wind
    solar_data = combined[combined['energy'] == 'solar_share']
    wind_data = combined[combined['energy'] == 'wind_share']
    
    # define energy_types
    energy_types = ['solar_share', 'wind_share']
    
    # Create subplots for each year
    fig = make_subplots(rows=len(solar_data["year"].unique()), cols=1, subplot_titles=[str(year) for year in solar_data['year'].unique()])

    # For each year, add a bar chart with operators on y-axis and share on x-axis
    for i, year in enumerate(solar_data['year'].unique()):
        # Add solar data
        fig.add_trace(go.Bar(
            x=solar_data[solar_data['year'] == year]['share_in_operator_production'], 
            y=solar_data[solar_data['year'] == year].index, 
            orientation='h', 
            name=f'Solar {year}', 
            marker_color='black',
            showlegend=False
        ), row=i+1, col=1)
        
        # Add wind data
        fig.add_trace(go.Bar(
            x=wind_data[wind_data['year'] == year]['share_in_operator_production'], 
            y=wind_data[wind_data['year'] == year].index, 
            orientation='h', 
            name=f'Wind {year}', 
            marker_color='grey',
            showlegend=False
        ), row=i+1, col=1)

    # Define the layout
    fig.update_layout(
        template=my_ibcs_template,
        title = 'Renewable Share by Operator',
        barmode='stack',  # Bars for the same y value will be stacked
        yaxis=dict(
            tickformat=',.0%',
            tickmode='array',
        ),
        xaxis=dict(
        )
    )
    
    fig.update_xaxes(range=[0, .6])


    return fig


# Load and aggregate data
monthly_data = load_and_aggregate_data()

# get the different charts
gridLoad = gridLoadChart()

# renewable increase
renewableInc = renewableIncrease()

# cpacity vs actual
capacityVsActual = renewable_share_by_operator()

edaLayout = html.Div(children=[
                        html.Div(children=[
                            
                            html.Div(children=[
                                dcc.Graph(id='load-diff', figure=gridLoad)
                                ], style={'width': '50%', 'height': '100%'}),
                            html.Div(children=[
                                dcc.Graph(id='capacity-vs-actual', figure=capacityVsActual)
                                ], style={'width': '50%', 'height': '150%'})
                            ], style={'display': 'flex'}),
                        
                        html.Div(children=[
                            dcc.Graph(id='renewable-increase', figure=renewableInc)
                            ], style={'width': '50%', 'height': '100%', 'align' : 'left'}),
                            ],
    )

