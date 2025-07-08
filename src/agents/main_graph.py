"""
Main LangGraph Workflow Definition for STONESOUP

This module assembles the complete agent workflow, connecting all nodes
and edges to create the document processing pipeline.
"""

import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.language_models import BaseLLM

from .state.agent_state import AgentState, create_initial_state, ProcessingStage
from .nodes.ingestion_node import IngestionNode
from .nodes.extraction_node import ExtractionNode
from .nodes.story_generation_node import StoryGenerationNode
from .nodes.validation_node import ValidationNode
from .edges.router import (
    route_after_ingestion,
    route_after_extraction,
    route_after_story_generation,
    route_after_validation,
    handle_error_routing
)
from .config import WorkflowConfig


logger = logging.getLogger("stonesoup.workflow")


class StoneSoupWorkflow:
    """
    Main workflow class for STONESOUP document processing.
    
    This class orchestrates the entire pipeline:
    1. Document Ingestion
    2. Entity/Information Extraction
    3. Story Generation
    4. Validation and Quality Scoring
    """
    
    def __init__(
        self,
        config: WorkflowConfig,
        llm: Optional[BaseLLM] = None,
        checkpointer: Optional[SqliteSaver] = None
    ):
        """
        Initialize the STONESOUP workflow.
        
        Args:
            config: Workflow configuration
            llm: Language model for nodes to use
            checkpointer: Optional checkpointer for state persistence
        """
        self.config = config
        self.llm = llm
        self.checkpointer = checkpointer or SqliteSaver.from_conn_string(":memory:")
        
        # Initialize nodes
        self.ingestion_node = IngestionNode(
            config=config.ingestion_config,
            llm=llm
        )
        
        self.extraction_node = ExtractionNode(
            config=config.extraction_config,
            llm=llm
        )
        
        self.story_generation_node = StoryGenerationNode(
            config=config.story_generation_config,
            llm=llm
        )
        
        self.validation_node = ValidationNode(
            config=config.validation_config,
            llm=llm
        )
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile(checkpointer=self.checkpointer)
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Configured StateGraph
        """
        # Create graph with AgentState
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("ingestion", self._wrap_node(self.ingestion_node))
        workflow.add_node("extraction", self._wrap_node(self.extraction_node))
        workflow.add_node("story_generation", self._wrap_node(self.story_generation_node))
        workflow.add_node("validation", self._wrap_node(self.validation_node))
        
        # Set entry point
        workflow.set_entry_point("ingestion")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "ingestion",
            route_after_ingestion,
            {
                "extraction": "extraction",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "extraction",
            route_after_extraction,
            {
                "story_generation": "story_generation",
                "validation": "validation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "story_generation",
            route_after_story_generation,
            {
                "validation": "validation",
                "extraction": "extraction",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "validation",
            route_after_validation,
            {
                "story_generation": "story_generation",
                "end": END
            }
        )
        
        return workflow
    
    def _wrap_node(self, node):
        """
        Wrap a node with error handling.
        
        Args:
            node: Node instance to wrap
            
        Returns:
            Wrapped node function
        """
        async def wrapped(state: AgentState) -> AgentState:
            try:
                return await node(state)
            except Exception as e:
                logger.error(f"Error in {node.config.name}: {e}", exc_info=True)
                
                # Let the node's error handling take care of state updates
                # but ensure we always return a state
                if hasattr(e, "state"):
                    return e.state
                else:
                    # Fallback error handling
                    state["error_messages"].append(f"Error in {node.config.name}: {str(e)}")
                    state["current_stage"] = ProcessingStage.FAILED
                    return state
        
        return wrapped
    
    async def process_document(
        self,
        document_id: str,
        content: str,
        source: str,
        document_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None
    ) -> AgentState:
        """
        Process a single document through the workflow.
        
        Args:
            document_id: Unique document identifier
            content: Document content
            source: Document source
            document_type: Type of document (optional)
            context: Additional context for processing (optional)
            thread_id: Thread ID for checkpointing (optional)
            
        Returns:
            Final agent state after processing
        """
        logger.info(
            f"Starting document processing",
            extra={
                "document_id": document_id,
                "source": source,
                "content_length": len(content)
            }
        )
        
        # Create initial state
        initial_state = create_initial_state(
            document_id=document_id,
            raw_content=content,
            source=source,
            document_type=document_type,
            max_retries=self.config.max_retries
        )
        
        # Add any additional context
        if context:
            initial_state["agent_context"].update(context)
        
        # Add workflow configuration to context
        initial_state["agent_context"]["min_confidence_threshold"] = self.config.min_confidence_threshold
        initial_state["agent_context"]["skip_story_generation"] = self.config.skip_story_generation
        
        # Configure thread
        config = {
            "configurable": {
                "thread_id": thread_id or document_id
            }
        }
        
        # Run the workflow
        start_time = datetime.utcnow()
        
        try:
            # Process through the graph
            final_state = await self.app.ainvoke(initial_state, config)
            
            # Log completion
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Document processing completed",
                extra={
                    "document_id": document_id,
                    "duration_seconds": duration,
                    "final_stage": final_state["current_stage"],
                    "confidence": final_state["confidence_scores"].overall,
                    "success": final_state["current_stage"] == ProcessingStage.COMPLETED
                }
            )
            
            return final_state
            
        except Exception as e:
            logger.error(
                f"Workflow failed for document {document_id}",
                exc_info=True
            )
            
            # Return state with error
            initial_state["current_stage"] = ProcessingStage.FAILED
            initial_state["error_messages"].append(f"Workflow error: {str(e)}")
            return initial_state
    
    async def process_batch(
        self,
        documents: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[AgentState]:
        """
        Process multiple documents concurrently.
        
        Args:
            documents: List of document dictionaries with keys:
                       document_id, content, source, document_type, context
            max_concurrent: Maximum concurrent document processing
            
        Returns:
            List of final states for each document
        """
        logger.info(f"Starting batch processing of {len(documents)} documents")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(doc):
            async with semaphore:
                return await self.process_document(
                    document_id=doc["document_id"],
                    content=doc["content"],
                    source=doc["source"],
                    document_type=doc.get("document_type"),
                    context=doc.get("context")
                )
        
        # Process all documents
        tasks = [process_with_semaphore(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        final_states = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process document {documents[i]['document_id']}: {result}")
                # Create error state
                error_state = create_initial_state(
                    document_id=documents[i]["document_id"],
                    raw_content=documents[i]["content"],
                    source=documents[i]["source"]
                )
                error_state["current_stage"] = ProcessingStage.FAILED
                error_state["error_messages"].append(str(result))
                final_states.append(error_state)
            else:
                final_states.append(result)
        
        # Log summary
        successful = sum(
            1 for state in final_states
            if state["current_stage"] == ProcessingStage.COMPLETED
        )
        
        logger.info(
            f"Batch processing completed",
            extra={
                "total": len(documents),
                "successful": successful,
                "failed": len(documents) - successful
            }
        )
        
        return final_states
    
    def get_workflow_state(self, thread_id: str) -> Optional[AgentState]:
        """
        Get the current state of a workflow thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Current state or None if not found
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            state = self.app.get_state(config)
            return state.values if state else None
        except Exception as e:
            logger.error(f"Failed to get state for thread {thread_id}: {e}")
            return None
    
    def get_workflow_history(self, thread_id: str) -> List[AgentState]:
        """
        Get the history of states for a workflow thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            List of historical states
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            history = []
            for state in self.app.get_state_history(config):
                history.append(state.values)
            return history
        except Exception as e:
            logger.error(f"Failed to get history for thread {thread_id}: {e}")
            return []


def create_workflow(
    config: Optional[WorkflowConfig] = None,
    llm: Optional[BaseLLM] = None,
    checkpoint_path: Optional[str] = None
) -> StoneSoupWorkflow:
    """
    Factory function to create a STONESOUP workflow.
    
    Args:
        config: Workflow configuration (uses default if not provided)
        llm: Language model instance
        checkpoint_path: Path for checkpoint database
        
    Returns:
        Configured StoneSoupWorkflow instance
    """
    if not config:
        config = WorkflowConfig()
    
    checkpointer = None
    if checkpoint_path:
        checkpointer = SqliteSaver.from_conn_string(checkpoint_path)
    
    return StoneSoupWorkflow(
        config=config,
        llm=llm,
        checkpointer=checkpointer
    )