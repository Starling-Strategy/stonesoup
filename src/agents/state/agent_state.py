"""
Agent State Model for STONESOUP LangGraph Workflow

This module defines the state that flows through the LangGraph workflow,
maintaining all necessary information as documents move through the
ingestion, extraction, story generation, and validation pipeline.
"""

from typing import Dict, List, Optional, Any, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStage(str, Enum):
    """Enum representing the current stage of document processing"""
    INGESTION = "ingestion"
    EXTRACTION = "extraction"
    STORY_GENERATION = "story_generation"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceScore(BaseModel):
    """Model for tracking confidence scores throughout the pipeline"""
    overall: float = Field(ge=0.0, le=1.0, description="Overall confidence score")
    extraction: Optional[float] = Field(None, ge=0.0, le=1.0, description="Extraction confidence")
    story_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Story quality score")
    validation: Optional[float] = Field(None, ge=0.0, le=1.0, description="Validation score")
    
    def update_overall(self) -> None:
        """Recalculate overall score based on component scores"""
        scores = [s for s in [self.extraction, self.story_quality, self.validation] if s is not None]
        if scores:
            self.overall = sum(scores) / len(scores)


class DocumentMetadata(BaseModel):
    """Metadata for ingested documents"""
    source: str = Field(description="Source of the document")
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    document_type: Optional[str] = Field(None, description="Type of document (pdf, text, etc)")
    page_count: Optional[int] = Field(None, description="Number of pages in document")
    word_count: Optional[int] = Field(None, description="Total word count")
    language: Optional[str] = Field(None, description="Detected language")


class ExtractedEntity(BaseModel):
    """Model for entities extracted from documents"""
    entity_type: str = Field(description="Type of entity (person, organization, location, etc)")
    name: str = Field(description="Entity name")
    context: str = Field(description="Context where entity was found")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional entity metadata")


class StoryElement(BaseModel):
    """Model for story elements generated from content"""
    element_type: str = Field(description="Type of story element (character, plot, setting, etc)")
    content: str = Field(description="Story element content")
    source_reference: Optional[str] = Field(None, description="Reference to source content")
    confidence: float = Field(ge=0.0, le=1.0, description="Generation confidence")


class ValidationResult(BaseModel):
    """Model for validation results"""
    is_valid: bool = Field(description="Whether content passed validation")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    score: float = Field(ge=0.0, le=1.0, description="Validation score")


class AgentState(TypedDict):
    """
    Main state object that flows through the LangGraph workflow.
    
    This state maintains all information as documents move through:
    1. Ingestion - Raw document processing
    2. Extraction - Entity and information extraction
    3. Story Generation - Creating narrative elements
    4. Validation - Quality checks and scoring
    """
    # Core document data
    document_id: str
    raw_content: str
    processed_content: Optional[str]
    
    # Processing metadata
    current_stage: ProcessingStage
    processing_history: List[Dict[str, Any]]
    error_messages: List[str]
    
    # Document metadata
    metadata: DocumentMetadata
    
    # Extraction results
    extracted_entities: List[ExtractedEntity]
    extracted_facts: List[Dict[str, Any]]
    key_themes: List[str]
    
    # Story generation results
    story_elements: List[StoryElement]
    generated_narrative: Optional[str]
    narrative_structure: Optional[Dict[str, Any]]
    
    # Validation results
    validation_result: Optional[ValidationResult]
    
    # Confidence tracking
    confidence_scores: ConfidenceScore
    
    # Control flags
    should_retry: bool
    retry_count: int
    max_retries: int
    
    # Additional context for agents
    agent_context: Dict[str, Any]


def create_initial_state(
    document_id: str,
    raw_content: str,
    source: str,
    document_type: Optional[str] = None,
    max_retries: int = 3
) -> AgentState:
    """
    Factory function to create an initial agent state for a new document.
    
    Args:
        document_id: Unique identifier for the document
        raw_content: Raw content of the document
        source: Source of the document
        document_type: Type of document (optional)
        max_retries: Maximum number of retries for failed operations
        
    Returns:
        Initialized AgentState ready for processing
    """
    metadata = DocumentMetadata(
        source=source,
        document_type=document_type,
        word_count=len(raw_content.split())
    )
    
    return AgentState(
        document_id=document_id,
        raw_content=raw_content,
        processed_content=None,
        current_stage=ProcessingStage.INGESTION,
        processing_history=[],
        error_messages=[],
        metadata=metadata,
        extracted_entities=[],
        extracted_facts=[],
        key_themes=[],
        story_elements=[],
        generated_narrative=None,
        narrative_structure=None,
        validation_result=None,
        confidence_scores=ConfidenceScore(overall=0.0),
        should_retry=False,
        retry_count=0,
        max_retries=max_retries,
        agent_context={}
    )


def add_processing_event(
    state: AgentState,
    event_type: str,
    details: Dict[str, Any],
    success: bool = True
) -> None:
    """
    Add a processing event to the state's history.
    
    Args:
        state: Current agent state
        event_type: Type of processing event
        details: Event details
        success: Whether the event was successful
    """
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "stage": state["current_stage"],
        "event_type": event_type,
        "success": success,
        "details": details
    }
    state["processing_history"].append(event)


def should_continue_processing(state: AgentState) -> bool:
    """
    Determine if processing should continue based on current state.
    
    Args:
        state: Current agent state
        
    Returns:
        True if processing should continue, False otherwise
    """
    # Check if we've reached a terminal stage
    if state["current_stage"] in [ProcessingStage.COMPLETED, ProcessingStage.FAILED]:
        return False
    
    # Check if we've exceeded retry limit
    if state["should_retry"] and state["retry_count"] >= state["max_retries"]:
        return False
    
    # Check confidence threshold (configurable)
    min_confidence = state["agent_context"].get("min_confidence_threshold", 0.3)
    if state["confidence_scores"].overall < min_confidence and state["retry_count"] > 0:
        return False
    
    return True