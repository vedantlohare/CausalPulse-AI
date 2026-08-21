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
            "cmo": "You are reporting to the Chief Marketing Officer. Focus on revenue loss, customer churn, and business impact. Avoid deep technical jargon.",
            "ops_lead": "You are reporting to the VP of Engineering. Focus on system failures, latency spikes, database locks, and technical root causes.",
            "analyst": "You are reporting to a Data Analyst. Provide a balanced view of both statistical anomalies and technical logs."
        }
        
        return role_prompts.get(role.lower(), "Provide a balanced executive summary.")

guardrails = GuardrailsRBAC()
