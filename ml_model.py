import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def run_anomaly_detection(df, features=['Nf1', 'Ng1', 'T451', 'TGT452'], contamination=0.01):
    """
    Runs Isolation Forest to detect statistical anomalies in engine parameters.
    contamination: The expected proportion of outliers in the dataset.
    """
    if df is None or df.empty:
        return df
        
    df_ml = df.copy()
    
    # Check if features exist in dataframe
    available_features = [f for f in features if f in df_ml.columns]
    
    if len(available_features) < 2:
        df_ml['Anomaly_ML'] = False
        return df_ml
        
    # We only want to run ML on the active phase where the engine is running
    # If 'Active' is not defined, we'll try to use Nf1 > 10
    if 'Active' in df_ml.columns:
        active_mask = df_ml['Active'] == True
    elif 'Nf1' in df_ml.columns:
        active_mask = pd.to_numeric(df_ml['Nf1'], errors='coerce') > 10
    else:
        active_mask = pd.Series(True, index=df_ml.index)
        
    # Extract data for modeling
    X = df_ml.loc[active_mask, available_features].copy()
    
    # Drop NaNs for the model
    X = X.dropna()
    
    if len(X) < 50: # Not enough data
        df_ml['Anomaly_ML'] = False
        return df_ml
        
    # Initialize and fit the model
    # using random_state for reproducibility
    model = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
    
    # Predict anomalies (-1 for anomalies, 1 for normal)
    preds = model.fit_predict(X)
    
    # Map predictions back to the dataframe
    X['Anomaly_ML'] = (preds == -1)
    
    # Initialize column with False
    df_ml['Anomaly_ML'] = False
    
    # Update the main dataframe using the index
    df_ml.loc[X.index, 'Anomaly_ML'] = X['Anomaly_ML']
    
    return df_ml
