import re

class GuardrailsRBAC:
    def __init__(self):
        # Basic regex patterns for PII
        self.patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "credit_card": r'\b(?:\d[ -]*?){13,16}\b'
        }
        
    def redact_pii(self, text: str) -> str:
        """
        Masks sensitive PII patterns before passing text to the LLM.
        """
        redacted = text
        for pii_type, pattern in self.patterns.items():
            redacted = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", redacted)
        return redacted
        
    def apply_role_context(self, role: str) -> str:
        """
        Returns a role-specific prompt prefix to ensure the LLM generates
        narratives tailored to the user's domain.
        """
        role_prompts = {
            "cmo": (
                "You are reporting to the Chief Marketing Officer (CMO). "
                "CRITICAL FOCUS: Frame the entire narrative around Revenue, Customer Experience, Brand Risk, and Churn. "
                "TONE: Urgent but business-focused. "
                "INSTRUCTIONS: DO NOT use technical jargon (e.g. 'redis', 'latency', 'queries'). Translate all technical failures into business consequences (e.g. 'checkout degradation')."
            ),
            "ops_lead": (
                "You are reporting to the VP of Engineering / Ops Lead. "
                "CRITICAL FOCUS: Frame the narrative around Infrastructure Health, SLA Breaches, Root Cause Nodes, and Mitigation. "
                "TONE: Highly technical, precise, and concise. "
                "INSTRUCTIONS: Explicitly name the failing microservices, databases, or API gateways. Reference the upstream topological dependency and recommend engineering interventions (e.g., failover, scaling)."
            ),
            "analyst": (
                "You are reporting to a Data Analyst. "
                "CRITICAL FOCUS: Frame the narrative around Statistical Z-scores, Standard Deviations, Baseline Shifts, and Data Quality. "
                "TONE: Analytical and mathematical. "
                "INSTRUCTIONS: Detail exactly how far the metric deviated from the expected baseline. If ambiguity is high, recommend specific SQL queries or statistical tests to run next."
            )
        }
        
        return role_prompts.get(role.lower(), "Provide a balanced executive summary.")

guardrails = GuardrailsRBAC()
