"""
Example usage of STONESOUP LangGraph Agent Infrastructure

This script demonstrates how to use the agent workflow for document processing.
"""

import asyncio
import logging
from typing import Optional

from langchain_openai import ChatOpenAI

from agents import (
    create_workflow,
    get_default_config,
    WorkflowConfig,
    ProcessingStage
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def process_single_document():
    """Example of processing a single document"""
    
    # Initialize LLM (replace with your preferred model)
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )
    
    # Get default configuration (options: "standard", "fast", "quality", "minimal")
    config = get_default_config("standard")
    
    # Create workflow
    workflow = create_workflow(
        config=config,
        llm=llm,
        checkpoint_path="stonesoup_checkpoints.db"  # Optional: persist state
    )
    
    # Example document
    document_content = """
    In a groundbreaking discovery, Dr. Sarah Chen and her team at Stanford University 
    have developed a new quantum computing algorithm that could revolutionize cryptography. 
    The breakthrough, announced at the International Conference on Quantum Computing in 
    Geneva last Tuesday, demonstrates a 1000x improvement in processing speed for certain 
    encryption tasks.
    
    "This changes everything we thought we knew about quantum encryption," said Dr. Chen 
    during her keynote speech. The algorithm, dubbed "QubitShield," has already attracted 
    interest from major tech companies including IBM and Google.
    
    The research, funded by a $5 million grant from the National Science Foundation, 
    took three years to complete. Initial tests show that QubitShield can break 
    traditional RSA encryption in minutes rather than years, raising both excitement 
    and concerns in the cybersecurity community.
    """
    
    # Process the document
    final_state = await workflow.process_document(
        document_id="doc_001",
        content=document_content,
        source="Stanford Research News",
        document_type="article",
        context={
            "topic": "quantum computing",
            "priority": "high"
        }
    )
    
    # Check results
    if final_state["current_stage"] == ProcessingStage.COMPLETED:
        print("\n✅ Document processed successfully!")
        print(f"\nConfidence Scores:")
        print(f"  - Overall: {final_state['confidence_scores'].overall:.2f}")
        print(f"  - Extraction: {final_state['confidence_scores'].extraction:.2f}")
        print(f"  - Story Quality: {final_state['confidence_scores'].story_quality:.2f}")
        print(f"  - Validation: {final_state['confidence_scores'].validation:.2f}")
        
        print(f"\nExtracted Entities: {len(final_state['extracted_entities'])}")
        for entity in final_state['extracted_entities'][:5]:
            print(f"  - {entity.name} ({entity.entity_type})")
        
        print(f"\nKey Themes: {', '.join(final_state['key_themes'])}")
        
        print(f"\nGenerated Narrative Preview:")
        print(final_state['generated_narrative'][:500] + "...")
        
        if final_state['validation_result']:
            print(f"\nValidation Score: {final_state['validation_result'].score:.2f}")
            if final_state['validation_result'].suggestions:
                print("Suggestions:")
                for suggestion in final_state['validation_result'].suggestions:
                    print(f"  - {suggestion}")
    else:
        print(f"\n❌ Document processing failed at stage: {final_state['current_stage']}")
        print(f"Errors: {final_state['error_messages']}")


async def process_batch_documents():
    """Example of processing multiple documents"""
    
    # Initialize components
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    config = get_default_config("fast")  # Use fast preset for batch processing
    workflow = create_workflow(config=config, llm=llm)
    
    # Example documents
    documents = [
        {
            "document_id": "batch_001",
            "content": "Apple Inc. announced record quarterly earnings...",
            "source": "Financial Times",
            "document_type": "report"
        },
        {
            "document_id": "batch_002",
            "content": "Climate scientists warn of accelerating ice melt...",
            "source": "Nature Journal",
            "document_type": "research_paper"
        },
        {
            "document_id": "batch_003",
            "content": "Interview with CEO Jane Smith on company transformation...",
            "source": "Business Weekly",
            "document_type": "interview"
        }
    ]
    
    # Process batch
    results = await workflow.process_batch(
        documents=documents,
        max_concurrent=3
    )
    
    # Summarize results
    successful = sum(1 for r in results if r["current_stage"] == ProcessingStage.COMPLETED)
    print(f"\nBatch Processing Complete: {successful}/{len(documents)} successful")
    
    for result in results:
        status = "✅" if result["current_stage"] == ProcessingStage.COMPLETED else "❌"
        print(f"{status} {result['document_id']}: {result['current_stage']}")


async def custom_configuration_example():
    """Example of using custom configuration"""
    
    # Create custom configuration
    custom_config = WorkflowConfig(
        name="custom_workflow",
        description="Custom configuration for specific use case",
        min_confidence_threshold=0.7,  # Higher confidence requirement
        skip_story_generation=False,
        quality_thresholds={
            "minimum_extraction_entities": 5,
            "minimum_extraction_facts": 10,
            "minimum_story_length": 500,
            "minimum_validation_score": 0.8
        }
    )
    
    # Customize node configurations
    custom_config.extraction_config.required_confidence = 0.8
    custom_config.extraction_config.timeout_seconds = 300
    
    custom_config.story_generation_config.temperature = 0.9
    custom_config.story_generation_config.max_retries = 4
    
    # Create workflow with custom config
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    workflow = create_workflow(config=custom_config, llm=llm)
    
    # Process document with custom settings
    final_state = await workflow.process_document(
        document_id="custom_001",
        content="Your document content here...",
        source="Custom Source",
        context={
            "require_high_quality": True,
            "narrative_style": "investigative"
        }
    )
    
    print(f"\nCustom workflow completed: {final_state['current_stage']}")


async def check_workflow_state():
    """Example of checking workflow state and history"""
    
    llm = ChatOpenAI(model="gpt-4")
    workflow = create_workflow(
        llm=llm,
        checkpoint_path="stonesoup_checkpoints.db"
    )
    
    # Check state of a previous run
    thread_id = "doc_001"  # Use the document_id as thread_id
    
    current_state = workflow.get_workflow_state(thread_id)
    if current_state:
        print(f"\nCurrent state for {thread_id}:")
        print(f"  Stage: {current_state['current_stage']}")
        print(f"  Confidence: {current_state['confidence_scores'].overall:.2f}")
        print(f"  Errors: {len(current_state['error_messages'])}")
    
    # Get history
    history = workflow.get_workflow_history(thread_id)
    print(f"\nWorkflow history: {len(history)} states")
    for i, state in enumerate(history[-3:]):  # Show last 3 states
        print(f"  State {i}: {state['current_stage']}")


def main():
    """Run examples"""
    import sys
    
    examples = {
        "single": process_single_document,
        "batch": process_batch_documents,
        "custom": custom_configuration_example,
        "state": check_workflow_state
    }
    
    # Get example to run from command line
    example = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    if example in examples:
        print(f"Running {example} example...")
        asyncio.run(examples[example]())
    else:
        print(f"Unknown example: {example}")
        print(f"Available examples: {', '.join(examples.keys())}")
        print("\nUsage: python example_usage.py [single|batch|custom|state]")


if __name__ == "__main__":
    main()