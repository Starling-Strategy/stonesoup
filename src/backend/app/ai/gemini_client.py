"""
Gemini AI client for STONESOUP.

This module provides:
- Text generation with Gemini Pro
- Embedding generation with text-embedding-004
- Retry logic and error handling
- Cost tracking and monitoring
"""
import os
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from tenacity import retry, stop_after_attempt, wait_exponential
import sentry_sdk
from pydantic import BaseModel, Field

from app.core.config import settings


# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))


class GeminiConfig(BaseModel):
    """Configuration for Gemini API calls."""
    model_name: str = Field(default="gemini-1.5-pro", description="Model to use for generation")
    embedding_model: str = Field(default="text-embedding-004", description="Model for embeddings")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    top_p: float = Field(default=0.95, ge=0.0, le=1.0, description="Top-p sampling")
    top_k: int = Field(default=40, ge=1, description="Top-k sampling")
    max_output_tokens: int = Field(default=2048, ge=1, description="Maximum tokens to generate")
    candidate_count: int = Field(default=1, ge=1, le=8, description="Number of candidates")


class GeminiResponse(BaseModel):
    """Response from Gemini API."""
    text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    usage: Dict[str, int]
    model: str
    finish_reason: str
    safety_ratings: Optional[Dict[str, Any]] = None


class EmbeddingResponse(BaseModel):
    """Response from embedding API."""
    embedding: List[float]
    model: str
    token_count: int


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI models.
    
    This client provides:
    - Async text generation
    - Embedding generation
    - Automatic retries with exponential backoff
    - Error tracking with Sentry
    - Cost estimation
    """
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        """Initialize the Gemini client with configuration."""
        self.config = config or GeminiConfig()
        
        # Initialize generation model
        self.generation_model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config={
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "max_output_tokens": self.config.max_output_tokens,
                "candidate_count": self.config.candidate_count,
            },
            # Safety settings - adjust based on your use case
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        # Track usage for cost monitoring
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_embedding_tokens = 0
        
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
    ) -> GeminiResponse:
        """
        Generate text using Gemini Pro.
        
        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            **kwargs: Override generation config parameters
            
        Returns:
            GeminiResponse with generated text and metadata
        """
        try:
            # Combine system instruction with prompt if provided
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            # Override config if kwargs provided
            generation_config = {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "max_output_tokens": kwargs.get("max_output_tokens", self.config.max_output_tokens),
            }
            
            # Generate response
            response = await asyncio.to_thread(
                self.generation_model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract response details
            candidate = response.candidates[0]
            
            # Calculate confidence score based on safety ratings and finish reason
            confidence_score = self._calculate_confidence(candidate)
            
            # Track token usage
            usage_metadata = response.usage_metadata
            self._total_input_tokens += usage_metadata.prompt_token_count
            self._total_output_tokens += usage_metadata.candidates_token_count
            
            return GeminiResponse(
                text=candidate.content.parts[0].text,
                confidence_score=confidence_score,
                usage={
                    "prompt_tokens": usage_metadata.prompt_token_count,
                    "completion_tokens": usage_metadata.candidates_token_count,
                    "total_tokens": usage_metadata.total_token_count
                },
                model=self.config.model_name,
                finish_reason=candidate.finish_reason.name,
                safety_ratings=self._extract_safety_ratings(candidate)
            )
            
        except Exception as e:
            # Log to Sentry
            sentry_sdk.capture_exception(e)
            
            # Re-raise with context
            raise Exception(f"Gemini generation failed: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_embedding(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> EmbeddingResponse:
        """
        Generate embeddings using text-embedding-004.
        
        Args:
            text: Text to embed
            task_type: Task type for embedding optimization
                      Options: RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, 
                              SEMANTIC_SIMILARITY, CLASSIFICATION, CLUSTERING
            
        Returns:
            EmbeddingResponse with embedding vector
        """
        try:
            # Generate embedding
            response = await asyncio.to_thread(
                genai.embed_content,
                model=f"models/{self.config.embedding_model}",
                content=text,
                task_type=task_type
            )
            
            # Track token usage (estimate based on text length)
            # Gemini uses roughly 1 token per 4 characters
            estimated_tokens = len(text) // 4
            self._total_embedding_tokens += estimated_tokens
            
            return EmbeddingResponse(
                embedding=response['embedding'],
                model=self.config.embedding_model,
                token_count=estimated_tokens
            )
            
        except Exception as e:
            # Log to Sentry
            sentry_sdk.capture_exception(e)
            
            # Re-raise with context
            raise Exception(f"Embedding generation failed: {str(e)}") from e
    
    async def batch_generate_embeddings(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
        batch_size: int = 100
    ) -> List[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            task_type: Task type for all embeddings
            batch_size: Number of texts to process in parallel
            
        Returns:
            List of EmbeddingResponse objects
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Generate embeddings in parallel
            tasks = [
                self.generate_embedding(text, task_type)
                for text in batch
            ]
            
            batch_embeddings = await asyncio.gather(*tasks)
            embeddings.extend(batch_embeddings)
            
            # Small delay between batches to avoid rate limits
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        return embeddings
    
    def _calculate_confidence(self, candidate) -> float:
        """
        Calculate confidence score based on response quality indicators.
        
        Factors:
        - Finish reason (STOP is best)
        - Safety ratings (lower is better)
        - Content presence
        """
        confidence = 1.0
        
        # Penalize non-STOP finish reasons
        if candidate.finish_reason.name != "STOP":
            confidence -= 0.3
            
        # Penalize high safety scores
        if hasattr(candidate, 'safety_ratings'):
            for rating in candidate.safety_ratings:
                if rating.probability.name in ["HIGH", "MEDIUM"]:
                    confidence -= 0.1
        
        # Ensure content exists
        if not candidate.content.parts or not candidate.content.parts[0].text:
            confidence = 0.0
            
        return max(0.0, min(1.0, confidence))
    
    def _extract_safety_ratings(self, candidate) -> Dict[str, Any]:
        """Extract safety ratings from candidate."""
        if not hasattr(candidate, 'safety_ratings'):
            return {}
            
        return {
            rating.category.name: rating.probability.name
            for rating in candidate.safety_ratings
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage statistics and estimated costs.
        
        Gemini pricing (as of 2024):
        - Input: $0.00025 per 1K tokens
        - Output: $0.00125 per 1K tokens  
        - Embeddings: $0.0001 per 1K tokens
        """
        input_cost = (self._total_input_tokens / 1000) * 0.00025
        output_cost = (self._total_output_tokens / 1000) * 0.00125
        embedding_cost = (self._total_embedding_tokens / 1000) * 0.0001
        
        return {
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_embedding_tokens": self._total_embedding_tokens,
            "estimated_cost": {
                "input": f"${input_cost:.4f}",
                "output": f"${output_cost:.4f}",
                "embeddings": f"${embedding_cost:.4f}",
                "total": f"${input_cost + output_cost + embedding_cost:.4f}"
            }
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_embedding_tokens = 0


# Global client instance
gemini_client = GeminiClient()


# Convenience functions
async def generate_text(prompt: str, **kwargs) -> str:
    """Quick text generation helper."""
    response = await gemini_client.generate_text(prompt, **kwargs)
    return response.text


async def generate_embedding(text: str) -> List[float]:
    """Quick embedding generation helper."""
    response = await gemini_client.generate_embedding(text)
    return response.embedding