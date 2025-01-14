import numpy as np
import pandas as pd
from supervised.automl import AutoML

# data source http://archive.ics.uci.edu/ml/datasets/Communities%20and%20Crime%20Unnormalized

df = pd.read_csv("tests/data/CrimeData/crimedata.csv", na_values=["?"])

X = df[df.columns[5:129]]
y = df["ViolentCrimesPerPop"]

sensitive_features = (df["racePctWhite"] > 84).astype(str)

automl = AutoML(
    #algorithms=["Decision Tree", "Neural Network", "Xgboost", "Linear", "CatBoost"],
    algorithms=["Xgboost", "Linear", "CatBoost"],
    train_ensemble=True,
    fairness_threshold=0.5,
)
automl.fit(X, y, sensitive_features=sensitive_features)
