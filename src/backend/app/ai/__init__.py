# AI/ML integrations for STONESOUP
# OpenRouter client provides access to multiple AI models including Gemini

from app.ai.openrouter_client import (
    openrouter_client,
    generate_text,
    generate_embedding,
    OpenRouterClient,
    OpenRouterConfig,
    OpenRouterResponse,
    EmbeddingResponse,
    GeminiCompatibleClient
)

# For backward compatibility, expose as gemini_client
gemini_client = openrouter_client

__all__ = [
    "openrouter_client",
    "gemini_client",  # Backward compatibility
    "generate_text",
    "generate_embedding",
    "OpenRouterClient",
    "OpenRouterConfig", 
    "OpenRouterResponse",
    "EmbeddingResponse",
    "GeminiCompatibleClient"
]