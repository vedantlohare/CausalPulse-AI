import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

def generate_telemetry():
    # 30 days of data, hourly
    dates = pd.date_range(start="2026-07-21", end="2026-08-20", freq="H")
    n = len(dates)
    
    # Base metrics (normal noise)
    redis_hit_rate = np.random.normal(0.95, 0.02, n)
    db_query_time = np.random.normal(45, 5, n) # ms
    api_latency = db_query_time + np.random.normal(20, 2, n) # ms
    checkout_success = np.random.normal(0.99, 0.005, n)
    revenue = np.random.normal(50000, 2000, n) # per hour

    # Introduce Anomaly around Aug 15, 10:00 AM to Aug 16, 10:00 AM
    anomaly_idx = (dates >= "2026-08-15 10:00:00") & (dates <= "2026-08-16 10:00:00")
    
    # The Chain of Events (Causal Graph):
    # Redis Hit Rate drops -> DB Query Time spikes -> API Latency Spikes -> Checkout Success Drops -> Revenue Drops
    redis_hit_rate[anomaly_idx] -= np.random.uniform(0.3, 0.5, sum(anomaly_idx)) # Huge drop in cache hits
    
    # DB Query time skyrockets due to cache miss
    db_query_time[anomaly_idx] += np.random.uniform(200, 400, sum(anomaly_idx))
    
    # API Latency skyrockets
    api_latency[anomaly_idx] = db_query_time[anomaly_idx] + np.random.uniform(50, 100, sum(anomaly_idx))
    
    # Checkout success drops because APIs timeout
    checkout_success[anomaly_idx] -= np.random.uniform(0.15, 0.30, sum(anomaly_idx))
    
    # Revenue drops
    revenue[anomaly_idx] -= np.random.uniform(15000, 25000, sum(anomaly_idx))
    
    # Clip values
    redis_hit_rate = np.clip(redis_hit_rate, 0, 1)
    checkout_success = np.clip(checkout_success, 0, 1)
    
    df = pd.DataFrame({
        "timestamp": dates,
        "region": ["US-East"] * n,
        "redis_hit_rate": redis_hit_rate,
        "db_query_time_ms": db_query_time,
        "api_latency_ms": api_latency,
        "checkout_success_rate": checkout_success,
        "hourly_revenue_usd": revenue
    })
    
    df.to_csv("enterprise_telemetry.csv", index=False)
    print("Generated enterprise_telemetry.csv")

def generate_logs():
    logs = [
        {
            "timestamp": "2026-08-15T09:45:00Z",
            "source": "Jira",
            "type": "Incident",
            "content": "[Minor] Redis cluster node upgrade scheduled for US-East region. Expecting seamless failover."
        },
        {
            "timestamp": "2026-08-15T10:15:00Z",
            "source": "Slack",
            "type": "DevOps Alert",
            "content": "@here PagerDuty Alert! Redis failover in US-East failed. Primary node offline. Cache hit rate plunging."
        },
        {
            "timestamp": "2026-08-15T11:00:00Z",
            "source": "Zendesk",
            "type": "Customer Ticket",
            "content": "Hi, our customers are complaining that the checkout page is just spinning and then timing out. Please help! My phone number is 555-123-4567 and my account is ACCT-9921."
        },
        {
            "timestamp": "2026-08-15T12:30:00Z",
            "source": "Zendesk",
            "type": "Customer Ticket",
            "content": "URGENT: Payments failing. We are losing sales. Account manager John Doe (johndoe@example.com) said this would be a reliable platform."
        },
        {
            "timestamp": "2026-08-16T09:30:00Z",
            "source": "Slack",
            "type": "DevOps Resolve",
            "content": "Redis nodes manually restarted and re-synced. Cache hit rate is recovering. DB load stabilizing."
        }
    ]
    
    with open("operational_logs.json", "w") as f:
        json.dump(logs, f, indent=4)
    print("Generated operational_logs.json")

if __name__ == "__main__":
    generate_telemetry()
    generate_logs()
