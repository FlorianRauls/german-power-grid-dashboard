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


# importing the dataset
path = os.path.join('data', 'results.sqlite')
conn = sqlite3.connect(path)

# Execute the first SQL statement to fetch every 2nd row from the database
query1 = """
SELECT
    *
FROM
    results
WHERE
    rowid % 2 = 0
"""

data = pd.read_sql_query(query1, conn)

# Close the connection
conn.close()


def calculate_MSE(actual, prediction):
    """
    Calculate the mean squared error between the actual and predicted values.
    """
    return np.square(np.subtract(actual, prediction)).mean().round(2)

# rename hour to stimestamp
data.rename(columns={'hour': 'utc_timestamp'}, inplace=True)

# for each prediction calculate the mean squared error
mse_entsoe = calculate_MSE(data['actual'], data['entsoe'])
mse_linReg = calculate_MSE(data['actual'], data['linReg'])
mse_rf = calculate_MSE(data['actual'], data['rf'])
mse_gb = calculate_MSE(data['actual'], data['gb'])
mse_perceptron = calculate_MSE(data['actual'], data['perceptron'])
mse_perceptron_more_dims = calculate_MSE(data['actual'], data['perceptronMoreDims'])

# bring mse into a more readable format (GWh)
mse_entsoe = str(round(mse_entsoe/1000000, 1)) + " TWh"
mse_linReg = str(round(mse_linReg/1000000, 1)) + " TWh"
mse_rf = str(round(mse_rf/1000000, 1)) + " TWh"
mse_gb = str(round(mse_gb/1000000, 1)) + " TWh"
mse_perceptron = str(round(mse_perceptron/1000000, 1)) + " TWh"
mse_perceptron_more_dims = str(round(mse_perceptron_more_dims/1000000, 1)) + " TWh"




# create subplots
titles = ["Ensoe Forecast (MSE: " + str(mse_entsoe) + ")", "Linear Regression (MSE: " + str(mse_linReg) + ")", "Random Forest Regression (MSE: " + str(mse_rf) + ")", "Gradient Boost (MSE: " + str(mse_gb) + ")", "Perceptron (MSE: " + str(mse_perceptron) + ")", "Perceptron with more dimensions (MSE: " + str(mse_perceptron_more_dims) + ")"]
fig = make_subplots(rows=2, cols=3, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=titles)


# add the actual load to the subplots
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=1, col=1)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=1, col=2)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=1, col=3)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=2, col=1)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=2, col=2)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['actual'], name='Actual Load'), row=2, col=3)

# fill with plots which compare actual load to the different forecasting models
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['entsoe'], name='Entsoe Forecast'), row=1, col=1)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['linReg'], name='Linear Regression'), row=1, col=2)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['rf'], name='Random Forest'), row=2, col=3)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['gb'], name='Gradient Boosting'), row=2, col=1)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['perceptron'], name='perceptron'), row=2, col=2)
fig.add_trace(go.Scatter(x=data['utc_timestamp'], y=data['perceptronMoreDims'], name='perceptron with more dimensions'), row=1, col=3)

# edit the layout
fig.update_layout(
    title='Actual Load vs. Forecasting Models',
    template=my_ibcs_template
)

start_date = "2019-01-02"
end_date = "2019-01-10"
fig.update_xaxes(range=[start_date, end_date])

ml_layout = html.Div(
    children=[
        dcc.Graph(
            id='chart',
            figure=fig,
            style={"width":"100%", "height":"100%"},
        )
    ])

