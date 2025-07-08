"""
OpenRouter AI client for STONESOUP.

This module provides a unified interface to multiple AI models through OpenRouter,
including Google's Gemini models, OpenAI, Anthropic, and others.

OpenRouter advantages:
- Single API for multiple providers
- Automatic fallbacks
- Cost optimization
- No need for individual API keys
"""
import os
from typing import List, Dict, Any, Optional, Tuple, Literal
import asyncio
from datetime import datetime
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import sentry_sdk
from pydantic import BaseModel, Field
import numpy as np

from app.core.config import settings


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter API calls."""
    # Model selection - can use any model available on OpenRouter
    model_name: str = Field(
        default="google/gemini-pro", 
        description="Model to use for generation"
    )
    embedding_model: str = Field(
        default="openai/text-embedding-3-small",  # More cost-effective than ada
        description="Model for embeddings"
    )
    
    # Generation parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=1)
    
    # OpenRouter specific
    route: Literal["fallback", "custom"] = Field(
        default="fallback",
        description="Routing strategy - fallback for reliability"
    )
    
    # Cost optimization
    max_cost_per_request: float = Field(
        default=0.10,
        description="Maximum cost per request in USD"
    )


class OpenRouterResponse(BaseModel):
    """Response from OpenRouter API."""
    text: str
    model: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    usage: Dict[str, int]
    cost: float
    finish_reason: str
    
    
class EmbeddingResponse(BaseModel):
    """Response from embedding API."""
    embeddings: List[List[float]]  # Can handle batch embeddings
    model: str
    token_count: int
    cost: float


class OpenRouterClient:
    """
    Client for interacting with AI models through OpenRouter.
    
    This provides access to:
    - Google Gemini models
    - OpenAI GPT models  
    - Anthropic Claude models
    - And many others
    
    All through a single unified API.
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """Initialize the OpenRouter client."""
        self.config = config or OpenRouterConfig()
        self.api_key = settings.OPENROUTER_API_KEY
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://stonesoup.ai",  # Required by OpenRouter
            "X-Title": "STONESOUP",  # Shows in OpenRouter dashboard
            "Content-Type": "application/json"
        }
        
        # Track usage for monitoring
        self._total_cost = 0.0
        self._request_count = 0
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> OpenRouterResponse:
        """
        Generate text using specified model through OpenRouter.
        
        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            **kwargs: Override generation config parameters
            
        Returns:
            OpenRouterResponse with generated text and metadata
        """
        try:
            # Build messages
            messages = []
            if system_instruction:
                messages.append({
                    "role": "system",
                    "content": system_instruction
                })
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Build request
            request_data = {
                "model": kwargs.get("model", self.config.model_name),
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "route": self.config.route,
                "transforms": ["middle-out"],  # OpenRouter optimization
            }
            
            # Make request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=request_data,
                    timeout=60.0
                )
                response.raise_for_status()
                
            data = response.json()
            
            # Extract response
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            # Calculate cost (OpenRouter provides this)
            cost = usage.get("total_cost", 0.0)
            self._total_cost += cost
            self._request_count += 1
            
            # Calculate confidence based on finish reason
            confidence = 1.0 if choice["finish_reason"] == "stop" else 0.7
            
            return OpenRouterResponse(
                text=choice["message"]["content"],
                model=data["model"],  # Actual model used (may differ due to fallback)
                confidence_score=confidence,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                cost=cost,
                finish_reason=choice["finish_reason"]
            )
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response else str(e)
            sentry_sdk.capture_exception(e)
            raise Exception(f"OpenRouter API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"OpenRouter generation failed: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            model: Optional model override
            
        Returns:
            Embedding vector
        """
        response = await self.generate_embeddings([text], model)
        return response.embeddings[0]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> EmbeddingResponse:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: Optional model override (defaults to config)
            
        Returns:
            EmbeddingResponse with all embeddings
        """
        try:
            model = model or self.config.embedding_model
            
            # OpenRouter embeddings endpoint
            request_data = {
                "model": model,
                "input": texts,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/embeddings",
                    headers=self.headers,
                    json=request_data,
                    timeout=60.0
                )
                response.raise_for_status()
                
            data = response.json()
            
            # Extract embeddings
            embeddings = [item["embedding"] for item in data["data"]]
            
            # Calculate cost
            usage = data.get("usage", {})
            cost = usage.get("total_cost", 0.0)
            self._total_cost += cost
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=data["model"],
                token_count=usage.get("total_tokens", 0),
                cost=cost
            )
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"OpenRouter embedding failed: {str(e)}") from e
    
    async def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 50,
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for large lists of texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            model: Optional model override
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.generate_embeddings(batch, model)
            all_embeddings.extend(response.embeddings)
            
            # Small delay between batches
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
                
        return all_embeddings
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models",
                headers=self.headers
            )
            response.raise_for_status()
            
        return response.json()["data"]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics and costs."""
        return {
            "total_requests": self._request_count,
            "total_cost": f"${self._total_cost:.4f}",
            "average_cost_per_request": f"${self._total_cost / max(1, self._request_count):.4f}",
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self._total_cost = 0.0
        self._request_count = 0


# Create a wrapper that matches the Gemini client interface
class GeminiCompatibleClient(OpenRouterClient):
    """
    OpenRouter client with Gemini-compatible interface.
    
    This allows us to use OpenRouter as a drop-in replacement
    for the Gemini client.
    """
    
    def __init__(self):
        # Use Gemini Pro through OpenRouter by default
        config = OpenRouterConfig(
            model_name="google/gemini-pro-1.5",  # Latest Gemini model
            embedding_model="openai/text-embedding-3-small",
            temperature=0.7,
            max_tokens=2048
        )
        super().__init__(config)
        
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> OpenRouterResponse:
        """Generate text with Gemini Pro via OpenRouter."""
        # Ensure we use Gemini unless explicitly overridden
        if "model" not in kwargs:
            kwargs["model"] = "google/gemini-pro-1.5"
        
        return await super().generate_text(prompt, system_instruction, **kwargs)


# Global client instance (replaces gemini_client)
openrouter_client = GeminiCompatibleClient()


# Update the convenience functions to match Gemini interface
async def generate_text(prompt: str, **kwargs) -> str:
    """Quick text generation helper."""
    response = await openrouter_client.generate_text(prompt, **kwargs)
    return response.text


async def generate_embedding(text: str) -> List[float]:
    """Quick embedding generation helper."""
    return await openrouter_client.generate_embedding(text)