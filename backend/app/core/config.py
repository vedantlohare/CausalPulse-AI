import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "CausalPulse AI"
    API_V1_STR: str = "/api/v1"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "DUMMY_KEY_FOR_MOCK")
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
settings = Settings()
