import os
import dotenv
from langchain_openai import ChatOpenAI, AzureChatOpenAI

class LlmFactory:
    """
    Modes:
      "local"  — your local LiteLLM proxy / Ollama / any OpenAI-compatible endpoint
      "groq"   — Groq cloud via OpenAI-compatible endpoint
      "azure"  — Azure OpenAI 
    """
    def __init__(self, mode: str = "local", temperature: float = 0.5):
        dotenv.load_dotenv()
        self.temperature = temperature
        self.mode = mode
        self._create_llm()

    def get_llm(self):
        return self.llm

    def _create_llm(self):
        if self.mode == "local":
            self.llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_ENDPOINT", "http://localhost:4000"),
                model=os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4-turbo"),
                temperature=self.temperature,
            )

        elif self.mode == "groq":
            self.llm = ChatOpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url=os.getenv("GROQ_ENDPOINT", "https://api.groq.com/openai/v1"),
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=self.temperature,
            )

        elif self.mode == "azure":
            self.llm = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                temperature=self.temperature,
            )

        else:
            raise ValueError(f"Unknown LLM mode: '{self.mode}'. Choose 'local', 'groq', or 'azure'.")