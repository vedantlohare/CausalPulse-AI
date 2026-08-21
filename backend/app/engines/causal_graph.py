import networkx as nx
import yaml
from pathlib import Path

class CausalGraphEngine:
    def __init__(self, contract_path: str = None):
        if contract_path is None:
            # Default to the schema directory
            base_dir = Path(__file__).resolve().parent.parent
            contract_path = base_dir / "schema" / "kpi_contract.yml"
            
        self.contract_path = contract_path
        self.kpi_config = self._load_contract()
        self.graph = self._build_dag()
        
    def _load_contract(self) -> dict:
        try:
            with open(self.contract_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Failed to load KPI contract: {e}")
            return {"kpis": {}, "levers": {}}
            
    def _build_dag(self) -> nx.DiGraph:
        """
        Builds a Directed Acyclic Graph (DAG) from the KPI contract dependencies.
        """
        G = nx.DiGraph()
        kpis = self.kpi_config.get('kpis', {})
        
        for kpi_name, config in kpis.items():
            G.add_node(kpi_name, **config)
            
            for upstream in config.get('upstream_dependencies', []):
                # Edge goes from Upstream -> Downstream (Cause -> Effect)
                G.add_edge(upstream, kpi_name)
                
        return G
        
    def trace_root_cause(self, anomalous_metrics: dict) -> list:
        """
        Given a set of metrics that are firing as anomalous, find the topological
        source node (the earliest cause in the chain).
        """
        if not anomalous_metrics:
            return []
            
        firing_nodes = set(anomalous_metrics.keys())
        
        # In our DAG, a root cause is a firing node that has no incoming edges 
        # from OTHER firing nodes.
        root_causes = []
        
        for node in firing_nodes:
            if node not in self.graph.nodes:
                continue
                
            # Get predecessors (upstream causes) of this node
            predecessors = set(self.graph.predecessors(node))
            
            # If none of its predecessors are also firing, this is a root cause
            if not (predecessors & firing_nodes):
                root_causes.append(node)
                
        return root_causes
        
    def simulate_lever(self, lever_name: str) -> dict:
        """
        Calculates the expected downstream impact of pulling a business lever.
        """
        levers = self.kpi_config.get('levers', {})
        if lever_name not in levers:
            return {"error": f"Lever {lever_name} not found"}
            
        lever = levers[lever_name]
        impacts = {}
        
        for primary_impact in lever.get('impacts', []):
            if primary_impact in self.graph.nodes:
                # Find all downstream KPIs this ultimately affects
                downstream = nx.descendants(self.graph, primary_impact)
                impacts[primary_impact] = {
                    "direct_improvement": lever.get('expected_improvement_pct'),
                    "downstream_metrics_affected": list(downstream)
                }
                
        return impacts

causal_graph = CausalGraphEngine()
