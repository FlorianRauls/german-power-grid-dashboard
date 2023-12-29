import torch as t
import sklearn as sk
import sqlite3
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import torch.nn as nn

def load_and_aggregate_data():
    
    path = os.path.join('data', 'cleaned_data.sqlite')
    conn = sqlite3.connect(path)
    
    # Query to fetch data from the database
    query = """
    SELECT 
        DE_load_actual_entsoe_transparency, 
        DE_load_forecast_entsoe_transparency, 
        year,
        month,
        day,
        hour,
        lag_1_hour
    FROM 
        cleaned_data;
    """
    
    df = pd.read_sql(query, conn)
    # replace nan with mean
    df["lag_1_hour"] = df["lag_1_hour"].fillna(df["lag_1_hour"].mean())
    df["DE_load_actual_entsoe_transparency"] = df["DE_load_actual_entsoe_transparency"].fillna(df["DE_load_actual_entsoe_transparency"].mean())

    return df


def train_linearRegression(trainX, trainY, testX, testY):
    """
    Train a linear regression model on the given data for hourly load prediction.
    """
    model = LinearRegression()
    train_X = trainX.values.reshape(-1, 1)
    train_Y = trainY.values.reshape(-1, 1)
    
    model.fit(train_X, train_Y)
    
    predictions = model.predict(testX.values.reshape(-1, 1))
    return predictions
    
    
def train_randomForest(trainX, trainY, testX, testY):
    """
    Train a random forest model on the given data for hourly load prediction.
    """
    model = RandomForestRegressor(n_estimators=500, max_depth=7, random_state=0, verbose=1)
    trainX = trainX.values.reshape(-1, 1)
    trainY = trainY.values.reshape(-1, 1)
    model.fit(trainX, trainY)
    testX = testX.values.reshape(-1, 1)
    predictions = model.predict(testX)
    return predictions


def train_gradientBoosting(trainX, trainY, testX, testY):
    """
    Train a gradient boosting model on the given data for hourly load prediction.
    """
    model = GradientBoostingRegressor(n_estimators=500, max_depth=7, random_state=0, verbose=1)
    trainX = trainX.values.reshape(-1, 1)
    trainY = trainY.values.reshape(-1, 1)
    model.fit(trainX, trainY)
    testX = testX.values.reshape(-1, 1)
    predictions = model.predict(testX)
    return predictions
    
def train_MultiLayerPerceptron(trainX, trainY, testX, testY):
    """
    Train a multi layer perceptron model on the given data for hourly load prediction.
    """
    model = nn.Sequential(
        nn.Linear(1, 100),
        nn.ReLU(),
        nn.Linear(100, 100),
        nn.ReLU(),
        nn.Linear(100, 1)
    )
    criterion = nn.MSELoss()
    optimizer = t.optim.Adam(model.parameters(), lr=0.25)
    trainX = t.Tensor(trainX.values.reshape(-1, 1))
    trainY = t.Tensor(trainY.values.reshape(-1, 1))
    for epoch in range(50):
        optimizer.zero_grad()
        outputs = model(trainX)
        loss = criterion(outputs, trainY)
        loss.backward()
        optimizer.step()
        print('epoch {}, loss {}'.format(epoch, loss.item()))
    testX = t.Tensor(testX.values.reshape(-1, 1))
    predictions = model(testX).detach().numpy()
    return predictions



if __name__ == "__main__":
    data = load_and_aggregate_data()
    # ignore data before 2015
    data = data[data["year"] >= 2015]
    before2019 = data[data["year"] < 2019]
    after2019 = data[data["year"] >= 2019]
    
    train, test = sk.model_selection.train_test_split(before2019, test_size=0.2)
    train_X = train["lag_1_hour"]
    test_X = after2019["lag_1_hour"]
    train_y = train["DE_load_actual_entsoe_transparency"]
    test_y = after2019["DE_load_actual_entsoe_transparency"]

    results = pd.DataFrame()
    results["hour"] = after2019["year"].astype(str) + "-" + after2019["month"].astype(str) + "-" + after2019["day"].astype(str) + " " + after2019["hour"].astype(str) + ":00:00"
    results["actual"] = test_y
    results["entsoe"] = after2019["DE_load_forecast_entsoe_transparency"]
    results["linReg"] = train_linearRegression(train_X, train_y, test_X, test_y)
    results["rf"] = train_randomForest(train_X, train_y, test_X, test_y)
    results["gb"] = train_gradientBoosting(train_X, train_y, test_X, test_y)
    results["perceptron"] = train_MultiLayerPerceptron(train_X, train_y, test_X, test_y)
    
    
    # save results to csv file
    results.to_csv(os.path.join("data", "results.csv"), index=False)
    