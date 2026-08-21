import yaml
from pathlib import Path

class FinancialQuantifier:
    def __init__(self, contract_path: str = None):
        if contract_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            contract_path = base_dir / "schema" / "kpi_contract.yml"
        
        self.contract_path = contract_path
        self._load_assumptions()
        
    def _load_assumptions(self):
        try:
            with open(self.contract_path, 'r') as f:
                contract = yaml.safe_load(f)
                assumptions = contract.get("financial_assumptions", {})
                self.avg_order_value = assumptions.get("avg_order_value_usd", 150.0)
                self.baseline_checkouts = assumptions.get("baseline_checkouts_per_hour", 1000)
        except Exception:
            self.avg_order_value = 150.0
            self.baseline_checkouts = 1000
        
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
            # Baseline loaded from contract
            lost_orders = self.baseline_checkouts * abs(delta) * duration_hours
            impact["financial_impact_usd"] = lost_orders * self.avg_order_value
            impact["description"] = f"Estimated {lost_orders:.0f} lost orders, draining ${impact['financial_impact_usd']:,.2f}."
        elif metric == "api_latency_ms":
            # Just to show different logic
            impact["description"] = f"API latency spiked by {delta:.1f}ms. Indirect revenue impact due to timeouts."
        else:
            impact["description"] = "Impact quantifiable via downstream dependencies."
            
        return impact

financial_quantifier = FinancialQuantifier()
