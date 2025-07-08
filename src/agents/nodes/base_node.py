"""
Base Node Class for STONESOUP LangGraph Agents

This module provides the base class for all agent nodes in the workflow,
implementing common functionality for error handling, logging, and state management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, List
import asyncio
import logging
from datetime import datetime
import traceback

from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from pydantic import BaseModel

from ..state.agent_state import AgentState, ProcessingStage, add_processing_event


class NodeConfig(BaseModel):
    """Configuration for a node"""
    name: str
    description: str
    max_retries: int = 3
    timeout_seconds: int = 300
    required_confidence: float = 0.7
    llm_model: Optional[str] = None
    temperature: float = 0.7


class BaseNode(ABC):
    """
    Abstract base class for all nodes in the STONESOUP LangGraph workflow.
    
    Provides common functionality:
    - Error handling and retry logic
    - Logging and monitoring
    - State validation and updates
    - LLM integration helpers
    - Async operation support
    """
    
    def __init__(
        self,
        config: NodeConfig,
        llm: Optional[BaseLLM] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base node.
        
        Args:
            config: Node configuration
            llm: Language model instance (optional)
            logger: Logger instance (optional)
        """
        self.config = config
        self.llm = llm
        self.logger = logger or logging.getLogger(f"stonesoup.{config.name}")
        self._execution_count = 0
        self._error_count = 0
    
    @abstractmethod
    async def _process(self, state: AgentState) -> AgentState:
        """
        Core processing logic to be implemented by subclasses.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        pass
    
    @abstractmethod
    def _validate_input(self, state: AgentState) -> List[str]:
        """
        Validate input state for this node.
        
        Args:
            state: Current agent state
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    async def __call__(self, state: AgentState) -> AgentState:
        """
        Execute the node with error handling and monitoring.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        start_time = datetime.utcnow()
        self._execution_count += 1
        
        try:
            # Log execution start
            self.logger.info(
                f"Starting {self.config.name} execution",
                extra={
                    "document_id": state["document_id"],
                    "stage": state["current_stage"],
                    "execution_count": self._execution_count
                }
            )
            
            # Validate input
            validation_errors = self._validate_input(state)
            if validation_errors:
                raise ValueError(f"Input validation failed: {', '.join(validation_errors)}")
            
            # Execute with timeout
            result_state = await asyncio.wait_for(
                self._process(state),
                timeout=self.config.timeout_seconds
            )
            
            # Add success event
            add_processing_event(
                result_state,
                event_type=f"{self.config.name}_completed",
                details={
                    "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "confidence": result_state["confidence_scores"].overall
                },
                success=True
            )
            
            return result_state
            
        except asyncio.TimeoutError:
            self._error_count += 1
            error_msg = f"{self.config.name} timed out after {self.config.timeout_seconds} seconds"
            self.logger.error(error_msg)
            return self._handle_error(state, error_msg, start_time)
            
        except Exception as e:
            self._error_count += 1
            error_msg = f"{self.config.name} failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._handle_error(state, error_msg, start_time, exception=e)
    
    def _handle_error(
        self,
        state: AgentState,
        error_msg: str,
        start_time: datetime,
        exception: Optional[Exception] = None
    ) -> AgentState:
        """
        Handle node execution errors.
        
        Args:
            state: Current agent state
            error_msg: Error message
            start_time: Execution start time
            exception: Exception instance (optional)
            
        Returns:
            Updated agent state with error information
        """
        # Add error to state
        state["error_messages"].append(error_msg)
        
        # Add error event
        add_processing_event(
            state,
            event_type=f"{self.config.name}_error",
            details={
                "error": error_msg,
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "traceback": traceback.format_exc() if exception else None
            },
            success=False
        )
        
        # Determine if we should retry
        if state["retry_count"] < state["max_retries"]:
            state["should_retry"] = True
            state["retry_count"] += 1
        else:
            state["current_stage"] = ProcessingStage.FAILED
        
        return state
    
    async def create_llm_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[BaseOutputParser] = None
    ):
        """
        Helper to create an LLM chain for use in node processing.
        
        Args:
            prompt_template: Prompt template for the chain
            output_parser: Optional output parser
            
        Returns:
            Configured LLM chain
        """
        if not self.llm:
            raise ValueError(f"LLM not configured for {self.config.name}")
        
        chain = prompt_template | self.llm
        
        if output_parser:
            chain = chain | output_parser
        
        return chain
    
    def extract_confidence_from_llm_response(
        self,
        response: Dict[str, Any],
        default: float = 0.5
    ) -> float:
        """
        Extract confidence score from LLM response.
        
        Args:
            response: LLM response dictionary
            default: Default confidence if not found
            
        Returns:
            Confidence score between 0 and 1
        """
        # Try common confidence field names
        confidence_fields = ["confidence", "confidence_score", "score", "certainty"]
        
        for field in confidence_fields:
            if field in response:
                try:
                    confidence = float(response[field])
                    return max(0.0, min(1.0, confidence))
                except (ValueError, TypeError):
                    continue
        
        return default
    
    def update_stage(
        self,
        state: AgentState,
        new_stage: ProcessingStage
    ) -> None:
        """
        Update the processing stage with logging.
        
        Args:
            state: Current agent state
            new_stage: New processing stage
        """
        old_stage = state["current_stage"]
        state["current_stage"] = new_stage
        
        self.logger.info(
            f"Stage transition: {old_stage} -> {new_stage}",
            extra={
                "document_id": state["document_id"],
                "old_stage": old_stage,
                "new_stage": new_stage
            }
        )
    
    def add_context(
        self,
        state: AgentState,
        key: str,
        value: Any
    ) -> None:
        """
        Add context information for downstream nodes.
        
        Args:
            state: Current agent state
            key: Context key
            value: Context value
        """
        state["agent_context"][f"{self.config.name}_{key}"] = value
    
    def get_context(
        self,
        state: AgentState,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve context information from state.
        
        Args:
            state: Current agent state
            key: Context key
            default: Default value if not found
            
        Returns:
            Context value or default
        """
        # First check node-specific context
        node_key = f"{self.config.name}_{key}"
        if node_key in state["agent_context"]:
            return state["agent_context"][node_key]
        
        # Then check general context
        return state["agent_context"].get(key, default)