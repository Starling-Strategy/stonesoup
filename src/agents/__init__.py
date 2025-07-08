"""
STONESOUP LangGraph Agent Infrastructure

This package provides the complete agent workflow for document processing,
including ingestion, extraction, story generation, and validation.
"""

from .main_graph import StoneSoupWorkflow, create_workflow
from .config import (
    WorkflowConfig,
    LLMConfig,
    DocumentConfig,
    ExtractionConfig,
    StoryConfig,
    ValidationConfig,
    get_default_config,
    load_config_from_file
)
from .state.agent_state import (
    AgentState,
    ProcessingStage,
    ConfidenceScore,
    DocumentMetadata,
    ExtractedEntity,
    StoryElement,
    ValidationResult,
    create_initial_state
)

__all__ = [
    # Main workflow
    "StoneSoupWorkflow",
    "create_workflow",
    
    # Configuration
    "WorkflowConfig",
    "LLMConfig",
    "DocumentConfig", 
    "ExtractionConfig",
    "StoryConfig",
    "ValidationConfig",
    "get_default_config",
    "load_config_from_file",
    
    # State models
    "AgentState",
    "ProcessingStage",
    "ConfidenceScore",
    "DocumentMetadata",
    "ExtractedEntity",
    "StoryElement",
    "ValidationResult",
    "create_initial_state"
]

__version__ = "0.1.0"