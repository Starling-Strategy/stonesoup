#!/usr/bin/env python3
"""
Test script to verify OpenRouter integration works correctly.

This script tests:
1. OpenRouter API connection
2. Text generation with multiple models
3. Embedding generation
4. Cost tracking
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai.openrouter_client import (
    openrouter_client,
    OpenRouterClient,
    OpenRouterConfig
)


async def test_basic_generation():
    """Test basic text generation."""
    print("=== Testing Basic Text Generation ===\n")
    
    try:
        # Test with default Gemini model
        print("📝 Testing Gemini Pro via OpenRouter...")
        response = await openrouter_client.generate_text(
            prompt="Write a haiku about artificial intelligence",
            system_instruction="You are a creative poet. Write only a haiku, nothing else."
        )
        
        print(f"✓ Generated text:\n{response.text}")
        print(f"  Model used: {response.model}")
        print(f"  Confidence: {response.confidence_score}")
        print(f"  Tokens: {response.usage}")
        print(f"  Cost: ${response.cost:.4f}")
        
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_embeddings():
    """Test embedding generation."""
    print("\n\n=== Testing Embedding Generation ===\n")
    
    try:
        texts = [
            "Machine learning engineer with expertise in NLP",
            "Data scientist specializing in computer vision",
            "Backend developer experienced with PostgreSQL"
        ]
        
        print(f"📊 Generating embeddings for {len(texts)} texts...")
        
        for text in texts:
            embedding = await openrouter_client.generate_embedding(text)
            print(f"✓ Text: '{text[:50]}...'")
            print(f"  Embedding dimensions: {len(embedding)}")
            print(f"  First 5 values: {embedding[:5]}")
            
    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_multiple_models():
    """Test using different models."""
    print("\n\n=== Testing Multiple Models ===\n")
    
    models = [
        ("google/gemini-pro-1.5", "Gemini Pro 1.5"),
        ("anthropic/claude-3-haiku", "Claude 3 Haiku"),
        ("openai/gpt-3.5-turbo", "GPT-3.5 Turbo")
    ]
    
    prompt = "Explain quantum computing in one sentence."
    
    for model_id, model_name in models:
        try:
            print(f"\n🤖 Testing {model_name}...")
            
            # Create custom client for this model
            config = OpenRouterConfig(model_name=model_id)
            client = OpenRouterClient(config)
            
            response = await client.generate_text(prompt)
            
            print(f"✓ {model_name} response:")
            print(f"  {response.text}")
            print(f"  Cost: ${response.cost:.4f}")
            
        except Exception as e:
            print(f"✗ {model_name} failed: {e}")


async def test_batch_embeddings():
    """Test batch embedding generation."""
    print("\n\n=== Testing Batch Embeddings ===\n")
    
    try:
        # Generate sample texts
        texts = [
            f"Test document {i}: This is a sample text for embedding generation"
            for i in range(10)
        ]
        
        print(f"🔄 Generating embeddings for {len(texts)} texts in batches...")
        
        embeddings = await openrouter_client.batch_generate_embeddings(
            texts, 
            batch_size=5
        )
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"  Each embedding has {len(embeddings[0].embedding)} dimensions")
        
    except Exception as e:
        print(f"✗ Batch embedding failed: {e}")
        import traceback
        traceback.print_exc()


async def test_usage_tracking():
    """Test usage and cost tracking."""
    print("\n\n=== Testing Usage Tracking ===\n")
    
    try:
        # Reset stats
        openrouter_client.reset_usage_stats()
        
        # Generate some usage
        await openrouter_client.generate_text("Count to 5")
        await openrouter_client.generate_embedding("Test embedding")
        
        # Get stats
        stats = openrouter_client.get_usage_stats()
        
        print("📊 Usage Statistics:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Total cost: {stats['total_cost']}")
        print(f"  Average cost per request: {stats['average_cost_per_request']}")
        
    except Exception as e:
        print(f"✗ Usage tracking failed: {e}")


async def test_available_models():
    """Test getting available models."""
    print("\n\n=== Testing Available Models ===\n")
    
    try:
        print("🔍 Fetching available models...")
        models = await openrouter_client.get_available_models()
        
        print(f"✓ Found {len(models)} available models")
        
        # Show first 5 models
        print("\nFirst 5 models:")
        for model in models[:5]:
            print(f"  - {model.get('id', 'unknown')}: {model.get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"✗ Failed to get models: {e}")


async def main():
    """Run all tests."""
    print("🚀 STONESOUP OpenRouter Integration Test\n")
    
    # Check for API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("⚠️  OPENROUTER_API_KEY not set in environment")
        print("   Please set OPENROUTER_API_KEY to test OpenRouter integration")
        return
    
    # Run tests
    await test_basic_generation()
    await test_embeddings()
    await test_multiple_models()
    await test_batch_embeddings()
    await test_usage_tracking()
    await test_available_models()
    
    print("\n\n✅ All tests completed!")
    
    # Final stats
    final_stats = openrouter_client.get_usage_stats()
    print(f"\n💰 Total test cost: {final_stats['total_cost']}")


if __name__ == "__main__":
    asyncio.run(main())