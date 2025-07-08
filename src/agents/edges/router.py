"""
Routing Logic for STONESOUP LangGraph Workflow

This module defines the edge functions and routing logic that determines
how the workflow transitions between different nodes based on state.
"""

from typing import Literal, Dict, Any, List
import logging

from ..state.agent_state import AgentState, ProcessingStage, should_continue_processing


logger = logging.getLogger("stonesoup.router")


def route_after_ingestion(state: AgentState) -> Literal["extraction", "end"]:
    """
    Route after ingestion node completes.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    # Check if we should continue processing
    if not should_continue_processing(state):
        logger.info(f"Ending workflow after ingestion for {state['document_id']}")
        return "end"
    
    # Check if we have processed content
    if not state.get("processed_content"):
        logger.error(f"No processed content available for {state['document_id']}")
        return "end"
    
    # Check confidence threshold
    if state["confidence_scores"].overall < 0.3:
        logger.warning(
            f"Low confidence after ingestion: {state['confidence_scores'].overall}"
        )
        return "end"
    
    # Proceed to extraction
    logger.info(f"Routing to extraction for {state['document_id']}")
    return "extraction"


def route_after_extraction(state: AgentState) -> Literal["story_generation", "validation", "end"]:
    """
    Route after extraction node completes.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    # Check if we should continue
    if not should_continue_processing(state):
        logger.info(f"Ending workflow after extraction for {state['document_id']}")
        return "end"
    
    # Check if we have enough extracted information
    entity_count = len(state.get("extracted_entities", []))
    fact_count = len(state.get("extracted_facts", []))
    
    if entity_count == 0 and fact_count == 0:
        logger.warning(f"No entities or facts extracted for {state['document_id']}")
        # Skip story generation and go to validation
        return "validation"
    
    # Check if story generation should be skipped (based on context)
    skip_story = state["agent_context"].get("skip_story_generation", False)
    if skip_story:
        logger.info(f"Skipping story generation for {state['document_id']}")
        return "validation"
    
    # Proceed to story generation
    logger.info(
        f"Routing to story generation for {state['document_id']} "
        f"(entities: {entity_count}, facts: {fact_count})"
    )
    return "story_generation"


def route_after_story_generation(state: AgentState) -> Literal["validation", "extraction", "end"]:
    """
    Route after story generation node completes.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    # Check if we should retry due to low quality
    if state.get("should_retry") and state["retry_count"] < state["max_retries"]:
        retry_from = state["agent_context"].get("retry_from_stage", "extraction")
        
        if retry_from == "extraction":
            logger.info(
                f"Retrying from extraction for {state['document_id']} "
                f"(attempt {state['retry_count'] + 1})"
            )
            state["current_stage"] = ProcessingStage.EXTRACTION
            return "extraction"
    
    # Check if narrative was generated
    if not state.get("generated_narrative"):
        logger.warning(f"No narrative generated for {state['document_id']}")
        return "end"
    
    # Proceed to validation
    logger.info(f"Routing to validation for {state['document_id']}")
    return "validation"


def route_after_validation(state: AgentState) -> Literal["story_generation", "end"]:
    """
    Route after validation node completes.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    validation_result = state.get("validation_result")
    
    if not validation_result:
        logger.error(f"No validation result for {state['document_id']}")
        return "end"
    
    # Check if validation passed
    if validation_result.is_valid:
        logger.info(
            f"Validation passed for {state['document_id']} "
            f"(score: {validation_result.score:.2f})"
        )
        return "end"
    
    # Check if we should retry
    if state.get("should_retry") and state["retry_count"] < state["max_retries"]:
        logger.info(
            f"Retrying story generation for {state['document_id']} "
            f"(attempt {state['retry_count'] + 1})"
        )
        # Reset the should_retry flag
        state["should_retry"] = False
        return "story_generation"
    
    # Validation failed and no more retries
    logger.warning(
        f"Validation failed for {state['document_id']} "
        f"(score: {validation_result.score:.2f})"
    )
    return "end"


def should_continue(state: AgentState) -> bool:
    """
    Determine if the workflow should continue.
    
    Args:
        state: Current agent state
        
    Returns:
        True if workflow should continue, False to end
    """
    # Check if we've reached a terminal stage
    if state["current_stage"] in [ProcessingStage.COMPLETED, ProcessingStage.FAILED]:
        return False
    
    # Check overall confidence
    min_confidence = state["agent_context"].get("min_confidence_threshold", 0.2)
    if state["confidence_scores"].overall < min_confidence:
        logger.warning(
            f"Confidence below threshold for {state['document_id']}: "
            f"{state['confidence_scores'].overall:.2f} < {min_confidence}"
        )
        return False
    
    # Check error count
    max_errors = state["agent_context"].get("max_errors", 10)
    if len(state.get("error_messages", [])) > max_errors:
        logger.error(
            f"Too many errors for {state['document_id']}: "
            f"{len(state['error_messages'])}"
        )
        return False
    
    return True


def get_next_node(state: AgentState) -> str:
    """
    Main routing function that determines the next node based on current state.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next node to execute
    """
    current_stage = state["current_stage"]
    
    routing_map = {
        ProcessingStage.INGESTION: route_after_ingestion,
        ProcessingStage.EXTRACTION: route_after_extraction,
        ProcessingStage.STORY_GENERATION: route_after_story_generation,
        ProcessingStage.VALIDATION: route_after_validation,
    }
    
    if current_stage in routing_map:
        return routing_map[current_stage](state)
    else:
        logger.error(f"Unknown stage: {current_stage}")
        return "end"


def create_conditional_edges() -> Dict[str, Any]:
    """
    Create conditional edge configuration for LangGraph.
    
    Returns:
        Dictionary of conditional edge configurations
    """
    return {
        "ingestion": route_after_ingestion,
        "extraction": route_after_extraction,
        "story_generation": route_after_story_generation,
        "validation": route_after_validation,
    }


def handle_error_routing(state: AgentState, error: Exception) -> str:
    """
    Handle routing when an error occurs in a node.
    
    Args:
        state: Current agent state
        error: Exception that occurred
        
    Returns:
        Next node to execute or "end"
    """
    logger.error(
        f"Error in {state['current_stage']} for {state['document_id']}: {error}"
    )
    
    # Add error to state
    state["error_messages"].append(str(error))
    
    # Check if we should retry
    if state["retry_count"] < state["max_retries"]:
        state["retry_count"] += 1
        state["should_retry"] = True
        
        # Determine which node to retry
        retry_same_node = state["agent_context"].get("retry_same_node", True)
        
        if retry_same_node:
            # Retry the same node
            return state["current_stage"].value
        else:
            # Go back to previous stage
            stage_order = [
                ProcessingStage.INGESTION,
                ProcessingStage.EXTRACTION,
                ProcessingStage.STORY_GENERATION,
                ProcessingStage.VALIDATION
            ]
            
            current_index = stage_order.index(state["current_stage"])
            if current_index > 0:
                previous_stage = stage_order[current_index - 1]
                state["current_stage"] = previous_stage
                return previous_stage.value
    
    # No more retries, end workflow
    state["current_stage"] = ProcessingStage.FAILED
    return "end"