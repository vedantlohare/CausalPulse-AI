import google.generativeai as genai
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using Gemini Pro for textual generation
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
    def generate_narrative(self, prompt: str, temperature: float = 0.3) -> tuple[str, dict]:
        """Generates narrative text and tracks tokens."""
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
            usage = getattr(response, "usage_metadata", None)
            if usage:
                token_usage = {
                    "prompt_tokens": getattr(usage, "prompt_token_count", 0),
                    "completion_tokens": getattr(usage, "candidates_token_count", 0),
                    "total_tokens": getattr(usage, "total_token_count", 0),
                    "is_mock": False
                }
            else:
                token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "is_mock": False}
                
            return response.text, token_usage
        except Exception as e:
            return f"Error generating narrative: {str(e)}", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "is_mock": False}
            
    def _mock_generation(self, prompt: str) -> tuple[str, dict]:
        """Returns a deterministic response for testing without a real API key."""
        narrative = "Based on the telemetry data, the root cause of the revenue drop is a spike in API latency, driven by DB query timeouts resulting from a Redis cache failure. Immediate action: Reroute traffic."
        # Simulated token counts for mock mode
        prompt_tokens = len(prompt) // 4
        completion_tokens = len(narrative) // 4
        token_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "is_mock": True
        }
        return narrative, token_usage

gemini_client = GeminiClient()
