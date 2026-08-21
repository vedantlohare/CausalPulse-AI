class FinancialQuantifier:
    def __init__(self):
        # Base financial values for simulation
        self.avg_order_value = 150.0
        self.cost_per_api_call = 0.001
        
    def quantify_impact(self, metric: str, delta: float, duration_hours: int = 1) -> dict:
        """
        Quantifies the financial impact of a metric delta.
        """
        impact = {
            "metric": metric,
            "delta": delta,
            "financial_impact_usd": 0.0,
            "description": ""
        }
        
        if metric == "hourly_revenue_usd":
            impact["financial_impact_usd"] = abs(delta) * duration_hours
            impact["description"] = f"Estimated drain of ${impact['financial_impact_usd']:,.2f} over {duration_hours} hour(s)."
        elif metric == "checkout_success_rate":
            # Assuming baseline of 1000 checkouts per hour
            lost_orders = 1000 * abs(delta) * duration_hours
            impact["financial_impact_usd"] = lost_orders * self.avg_order_value
            impact["description"] = f"Estimated {lost_orders:.0f} lost orders, draining ${impact['financial_impact_usd']:,.2f}."
        elif metric == "api_latency_ms":
            # Just to show different logic
            impact["description"] = f"API latency spiked by {delta:.1f}ms. Indirect revenue impact due to timeouts."
        else:
            impact["description"] = "Impact quantifiable via downstream dependencies."
            
        return impact

financial_quantifier = FinancialQuantifier()
