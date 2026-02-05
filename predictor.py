import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_usage(data_log, metric='cpu'):
    if len(data_log) < 10:  # حداقل داده
        return 0
    
    df = pd.DataFrame(data_log)
    df['timestamp'] = pd.to_datetime(df['time']).astype(int) / 10**9  # unix time برای رگرسیون
    X = df['timestamp'].values[-60:].reshape(-1, 1)  # آخرین ۶۰ داده
    y = df[metric].values[-60:]
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_time = df['timestamp'].iloc[-1] + 60  # ۱ دقیقه آینده
    pred = model.predict([[future_time]])
    return pred[0]