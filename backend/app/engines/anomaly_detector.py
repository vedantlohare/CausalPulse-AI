import pandas as pd
import numpy as np

class AnomalyDetector:
    def __init__(self, z_score_threshold: float = 3.0):
        self.z_score_threshold = z_score_threshold
        
    def detect_anomalies(self, df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
        """
        Identifies anomalies using Z-score on a rolling window.
        In a real prod system, we'd use STL or Bayesian structural time series here.
        """
        # Ensure it's sorted by time
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by="timestamp")
        
        # Calculate rolling mean and std
        rolling_mean = df[metric_col].rolling(window=24, min_periods=1).mean()
        rolling_std = df[metric_col].rolling(window=24, min_periods=1).std().replace(0, 1e-9)
        
        # Calculate Z-score
        z_scores = (df[metric_col] - rolling_mean) / rolling_std
        
        # Flag anomalies
        df['is_anomaly'] = z_scores.abs() > self.z_score_threshold
        df['z_score'] = z_scores
        df['baseline'] = rolling_mean
        
        return df
        
    def get_latest_anomalies(self, df: pd.DataFrame, window_hours: int = 24) -> dict:
        """
        Returns a dictionary of metrics that have anomalies in the latest window.
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Get data from the last window_hours
        latest_time = df['timestamp'].max()
        cutoff_time = latest_time - pd.Timedelta(hours=window_hours)
        recent_df = df[df['timestamp'] >= cutoff_time]

        
        numeric_cols = [c for c in df.columns if df[c].dtype in [np.float64, np.int64]]
        anomalies = {}
        
        for col in numeric_cols:
            annotated_df = self.detect_anomalies(recent_df, col)
            anomaly_rows = annotated_df[annotated_df['is_anomaly']]
            if not anomaly_rows.empty:
                # Find the maximum deviation
                max_row = anomaly_rows.loc[anomaly_rows['z_score'].abs().idxmax()]
                anomalies[col] = {
                    "timestamp": max_row['timestamp'],
                    "value": max_row[col],
                    "baseline": max_row['baseline'],
                    "z_score": max_row['z_score'],
                    "direction": "spike" if max_row['z_score'] > 0 else "drop"
                }
                
        return anomalies

anomaly_detector = AnomalyDetector()
