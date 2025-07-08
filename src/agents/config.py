"""
Configuration for STONESOUP LangGraph Agents

This module defines configuration classes and defaults for the agent workflow,
allowing customization of behavior, thresholds, and processing parameters.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .nodes.base_node import NodeConfig


class WorkflowConfig(BaseModel):
    """Main configuration for the STONESOUP workflow"""
    
    # General workflow settings
    name: str = Field(default="stonesoup_workflow", description="Workflow name")
    description: str = Field(
        default="Document processing pipeline for story generation",
        description="Workflow description"
    )
    max_retries: int = Field(default=3, description="Maximum retries per document")
    min_confidence_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to continue processing"
    )
    
    # Processing options
    skip_story_generation: bool = Field(
        default=False,
        description="Skip story generation and go directly to validation"
    )
    enable_checkpointing: bool = Field(
        default=True,
        description="Enable state checkpointing"
    )
    
    # Node configurations
    ingestion_config: NodeConfig = Field(
        default_factory=lambda: NodeConfig(
            name="ingestion_node",
            description="Document ingestion and preprocessing",
            max_retries=3,
            timeout_seconds=120,
            required_confidence=0.6,
            temperature=0.3
        )
    )
    
    extraction_config: NodeConfig = Field(
        default_factory=lambda: NodeConfig(
            name="extraction_node",
            description="Entity and information extraction",
            max_retries=3,
            timeout_seconds=180,
            required_confidence=0.7,
            temperature=0.5
        )
    )
    
    story_generation_config: NodeConfig = Field(
        default_factory=lambda: NodeConfig(
            name="story_generation_node",
            description="Story and narrative generation",
            max_retries=2,
            timeout_seconds=240,
            required_confidence=0.75,
            temperature=0.8
        )
    )
    
    validation_config: NodeConfig = Field(
        default_factory=lambda: NodeConfig(
            name="validation_node",
            description="Content validation and quality scoring",
            max_retries=2,
            timeout_seconds=120,
            required_confidence=0.8,
            temperature=0.3
        )
    )
    
    # Performance settings
    batch_size: int = Field(default=10, description="Batch size for concurrent processing")
    max_concurrent: int = Field(default=5, description="Maximum concurrent document processing")
    
    # Quality thresholds
    quality_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "minimum_extraction_entities": 3,
            "minimum_extraction_facts": 5,
            "minimum_story_length": 200,
            "minimum_validation_score": 0.6,
            "good_validation_score": 0.8,
            "excellent_validation_score": 0.9
        }
    )
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True


class LLMConfig(BaseModel):
    """Configuration for LLM usage"""
    
    model_name: str = Field(default="gpt-4", description="LLM model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens per request")
    timeout: int = Field(default=60, description="LLM request timeout in seconds")
    
    # Model-specific settings for different tasks
    ingestion_temperature: float = Field(default=0.3, description="Temperature for ingestion")
    extraction_temperature: float = Field(default=0.5, description="Temperature for extraction")
    story_temperature: float = Field(default=0.8, description="Temperature for story generation")
    validation_temperature: float = Field(default=0.3, description="Temperature for validation")
    
    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum LLM request retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")


class DocumentConfig(BaseModel):
    """Configuration for document processing"""
    
    # Size limits
    max_document_size: int = Field(
        default=100000,
        description="Maximum document size in characters"
    )
    chunk_size: int = Field(
        default=3000,
        description="Size of chunks for processing large documents"
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between chunks"
    )
    
    # Processing options
    detect_language: bool = Field(
        default=True,
        description="Automatically detect document language"
    )
    normalize_text: bool = Field(
        default=True,
        description="Normalize text during ingestion"
    )
    extract_metadata: bool = Field(
        default=True,
        description="Extract document metadata"
    )
    
    # Supported formats
    supported_formats: list[str] = Field(
        default_factory=lambda: ["txt", "pdf", "docx", "html", "md"],
        description="Supported document formats"
    )


class ExtractionConfig(BaseModel):
    """Configuration for entity and information extraction"""
    
    # Entity extraction settings
    entity_types: list[str] = Field(
        default_factory=lambda: [
            "PERSON", "ORG", "LOC", "EVENT", 
            "TIME", "PRODUCT", "CONCEPT"
        ],
        description="Entity types to extract"
    )
    
    max_entities_per_type: int = Field(
        default=50,
        description="Maximum entities to extract per type"
    )
    
    # Fact extraction settings
    max_facts: int = Field(
        default=30,
        description="Maximum facts to extract"
    )
    
    fact_min_length: int = Field(
        default=20,
        description="Minimum fact length in characters"
    )
    
    fact_max_length: int = Field(
        default=300,
        description="Maximum fact length in characters"
    )
    
    # Theme extraction settings
    max_themes: int = Field(
        default=5,
        description="Maximum themes to identify"
    )
    
    # Relationship extraction
    extract_relationships: bool = Field(
        default=True,
        description="Extract entity relationships"
    )
    
    max_relationships: int = Field(
        default=20,
        description="Maximum relationships to extract"
    )


class StoryConfig(BaseModel):
    """Configuration for story generation"""
    
    # Narrative settings
    narrative_styles: list[str] = Field(
        default_factory=lambda: [
            "investigative", "biographical", "dramatic",
            "informative", "analytical"
        ],
        description="Available narrative styles"
    )
    
    default_style: str = Field(
        default="investigative",
        description="Default narrative style"
    )
    
    # Length constraints
    min_story_length: int = Field(
        default=200,
        description="Minimum story length in words"
    )
    
    max_story_length: int = Field(
        default=2000,
        description="Maximum story length in words"
    )
    
    # Story elements
    include_dialogue: bool = Field(
        default=True,
        description="Include dialogue in stories when appropriate"
    )
    
    include_descriptions: bool = Field(
        default=True,
        description="Include descriptive elements"
    )
    
    maintain_chronology: bool = Field(
        default=True,
        description="Maintain chronological order"
    )
    
    # Creativity settings
    creativity_level: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Level of creative interpretation (0=factual, 1=creative)"
    )


class ValidationConfig(BaseModel):
    """Configuration for content validation"""
    
    # Validation criteria weights
    criteria_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "factual_accuracy": 0.3,
            "narrative_coherence": 0.2,
            "completeness": 0.2,
            "clarity": 0.1,
            "entity_coverage": 0.1,
            "theme_integration": 0.1
        },
        description="Weights for different validation criteria"
    )
    
    # Thresholds
    passing_score: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum score to pass validation"
    )
    
    # Validation checks
    check_factual_accuracy: bool = Field(
        default=True,
        description="Verify facts against source"
    )
    
    check_entity_coverage: bool = Field(
        default=True,
        description="Check entity coverage percentage"
    )
    
    check_readability: bool = Field(
        default=True,
        description="Assess readability metrics"
    )
    
    # Coverage requirements
    min_entity_coverage: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum percentage of entities to include"
    )
    
    min_fact_coverage: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum percentage of facts to include"
    )


def load_config_from_file(config_path: str) -> WorkflowConfig:
    """
    Load workflow configuration from a JSON or YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        WorkflowConfig instance
    """
    import json
    import yaml
    from pathlib import Path
    
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if path.suffix == ".json":
        with open(path, "r") as f:
            config_data = json.load(f)
    elif path.suffix in [".yaml", ".yml"]:
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {path.suffix}")
    
    return WorkflowConfig(**config_data)


# Default configurations for different use cases
DEFAULT_CONFIGS = {
    "standard": WorkflowConfig(),
    
    "fast": WorkflowConfig(
        ingestion_config=NodeConfig(
            name="ingestion_node",
            description="Fast ingestion",
            timeout_seconds=60,
            required_confidence=0.5
        ),
        extraction_config=NodeConfig(
            name="extraction_node",
            description="Fast extraction",
            timeout_seconds=90,
            required_confidence=0.6
        ),
        story_generation_config=NodeConfig(
            name="story_generation_node",
            description="Fast story generation",
            timeout_seconds=120,
            required_confidence=0.65,
            temperature=0.7
        ),
        validation_config=NodeConfig(
            name="validation_node",
            description="Fast validation",
            timeout_seconds=60,
            required_confidence=0.7
        )
    ),
    
    "quality": WorkflowConfig(
        min_confidence_threshold=0.5,
        quality_thresholds={
            "minimum_extraction_entities": 5,
            "minimum_extraction_facts": 10,
            "minimum_story_length": 500,
            "minimum_validation_score": 0.8,
            "good_validation_score": 0.9,
            "excellent_validation_score": 0.95
        },
        extraction_config=NodeConfig(
            name="extraction_node",
            description="High-quality extraction",
            timeout_seconds=300,
            required_confidence=0.8,
            max_retries=5
        ),
        story_generation_config=NodeConfig(
            name="story_generation_node",
            description="High-quality story generation",
            timeout_seconds=360,
            required_confidence=0.85,
            temperature=0.9,
            max_retries=4
        )
    ),
    
    "minimal": WorkflowConfig(
        skip_story_generation=True,
        min_confidence_threshold=0.2,
        ingestion_config=NodeConfig(
            name="ingestion_node",
            description="Minimal ingestion",
            max_retries=1,
            timeout_seconds=30
        ),
        extraction_config=NodeConfig(
            name="extraction_node",
            description="Minimal extraction",
            max_retries=1,
            timeout_seconds=60
        )
    )
}


def get_default_config(preset: str = "standard") -> WorkflowConfig:
    """
    Get a default configuration preset.
    
    Args:
        preset: Configuration preset name
        
    Returns:
        WorkflowConfig instance
    """
    if preset not in DEFAULT_CONFIGS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(DEFAULT_CONFIGS.keys())}")
    
    return DEFAULT_CONFIGS[preset].copy()