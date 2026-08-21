import google.generativeai as genai
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using Gemini Pro for textual generation
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
    def generate_narrative(self, prompt: str, temperature: float = 0.3) -> str:
        """Generates narrative text and tracks tokens (simulated for now)."""
        try:
            # We would normally track actual tokens returned by the API here.
            # Using a mock generation if dummy key is used to prevent failures during dev.
            if settings.GEMINI_API_KEY == "DUMMY_KEY_FOR_MOCK":
                return self._mock_generation(prompt)
                
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            return response.text
        except Exception as e:
            return f"Error generating narrative: {str(e)}"
            
    def _mock_generation(self, prompt: str) -> str:
        """Returns a deterministic response for testing without a real API key."""
        return "Based on the telemetry data, the root cause of the revenue drop is a spike in API latency, driven by DB query timeouts resulting from a Redis cache failure. Immediate action: Reroute traffic."

gemini_client = GeminiClient()
