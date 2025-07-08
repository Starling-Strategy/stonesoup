"""
Story Generation Node for STONESOUP LangGraph Workflow

This node generates narrative elements and stories from extracted entities and facts,
transforming structured information into compelling narratives.
"""

from typing import List, Dict, Any, Optional
import random
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .base_node import BaseNode, NodeConfig
from ..state.agent_state import AgentState, ProcessingStage, StoryElement


class NarrativeStructure(BaseModel):
    """Model for narrative structure"""
    narrative_type: str = Field(description="Type of narrative (chronological, thematic, character-driven, etc)")
    main_characters: List[str] = Field(description="Main characters/entities in the story")
    central_conflict: str = Field(description="Central conflict or tension")
    key_events: List[str] = Field(description="Key events in chronological order")
    themes: List[str] = Field(description="Narrative themes")
    tone: str = Field(description="Narrative tone (investigative, dramatic, informative, etc)")


class GeneratedStory(BaseModel):
    """Model for generated story output"""
    title: str = Field(description="Story title")
    narrative: str = Field(description="Complete narrative text")
    structure: NarrativeStructure = Field(description="Narrative structure")
    story_elements: List[Dict[str, str]] = Field(description="Individual story elements")
    confidence: float = Field(ge=0.0, le=1.0, description="Generation confidence")


class StoryGenerationNode(BaseNode):
    """
    Node responsible for generating stories and narratives from extracted information.
    
    Key responsibilities:
    - Transform entities and facts into narrative elements
    - Create compelling story structures
    - Generate coherent narratives
    - Maintain factual accuracy while enhancing readability
    """
    
    def __init__(self, config: Optional[NodeConfig] = None, **kwargs):
        """Initialize story generation node with default config if not provided"""
        if not config:
            config = NodeConfig(
                name="story_generation_node",
                description="Story and narrative generation",
                max_retries=2,
                timeout_seconds=240,
                required_confidence=0.75,
                temperature=0.8  # Higher temperature for creative generation
            )
        super().__init__(config, **kwargs)
        
        # Story generation prompt
        self.story_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a master storyteller and narrative architect. Transform the provided entities, facts, and themes into a compelling narrative.

            Guidelines:
            1. ACCURACY: Stay true to the facts while crafting an engaging narrative
            2. STRUCTURE: Create a clear narrative arc with beginning, middle, and end
            3. CHARACTERS: Develop the entities into compelling characters with motivations
            4. CONFLICT: Identify and highlight tensions, conflicts, or challenges
            5. THEMES: Weave the identified themes throughout the narrative
            6. TONE: Match the tone to the content (investigative for scandals, inspiring for achievements, etc.)
            
            Create a narrative that:
            - Engages readers from the first sentence
            - Maintains factual accuracy
            - Provides context and background
            - Builds tension and resolution
            - Concludes with impact
            
            Also provide the narrative structure and individual story elements."""),
            ("human", """Entities: {entities}
            
            Facts: {facts}
            
            Themes: {themes}
            
            Document Context: {context}
            
            Generate a compelling narrative from this information.""")
        ])
        
        self.story_parser = PydanticOutputParser(pydantic_object=GeneratedStory)
        
        # Narrative templates for different story types
        self.narrative_templates = {
            "investigation": "uncovering hidden truths and exposing wrongdoing",
            "biography": "exploring the life and impact of remarkable individuals",
            "conflict": "examining tensions and their resolution",
            "discovery": "revealing new insights and breakthroughs",
            "transformation": "chronicling change and evolution"
        }
    
    def _validate_input(self, state: AgentState) -> List[str]:
        """Validate input state for story generation"""
        errors = []
        
        if state["current_stage"] != ProcessingStage.STORY_GENERATION:
            errors.append(f"Invalid stage for story generation: {state['current_stage']}")
        
        if not state.get("extracted_entities") and not state.get("extracted_facts"):
            errors.append("No entities or facts available for story generation")
        
        return errors
    
    async def _process(self, state: AgentState) -> AgentState:
        """
        Generate stories from extracted information.
        
        Steps:
        1. Analyze available entities and facts
        2. Determine narrative structure
        3. Generate story elements
        4. Create complete narrative
        """
        self.logger.info(f"Starting story generation for document {state['document_id']}")
        
        # Prepare input data
        entities = state["extracted_entities"]
        facts = state["extracted_facts"]
        themes = state["key_themes"]
        
        # Get document context
        doc_summary = self.get_context(state, "document_summary", "")
        doc_type = state["metadata"].document_type
        
        if self.llm:
            # Generate story using LLM
            story_result = await self._generate_story_with_llm(
                entities, facts, themes, doc_summary
            )
            
            # Store generated narrative
            state["generated_narrative"] = story_result.narrative
            state["narrative_structure"] = story_result.structure.dict()
            
            # Convert story elements to StoryElement objects
            state["story_elements"] = [
                StoryElement(
                    element_type=elem.get("type", "scene"),
                    content=elem.get("content", ""),
                    source_reference=elem.get("source", None),
                    confidence=elem.get("confidence", 0.8)
                )
                for elem in story_result.story_elements
            ]
            
            # Update confidence
            state["confidence_scores"].story_quality = story_result.confidence
            
        else:
            # Fallback to template-based generation
            narrative = self._generate_story_basic(entities, facts, themes, doc_type)
            state["generated_narrative"] = narrative
            
            # Create basic story elements
            state["story_elements"] = self._create_basic_story_elements(
                entities, facts, themes
            )
            
            state["confidence_scores"].story_quality = 0.6
        
        # Update overall confidence
        state["confidence_scores"].update_overall()
        
        # Add generation metrics to context
        self.add_context(state, "narrative_length", len(state["generated_narrative"]))
        self.add_context(state, "story_elements_count", len(state["story_elements"]))
        
        # Update stage
        self.update_stage(state, ProcessingStage.VALIDATION)
        
        self.logger.info(
            f"Story generation complete for {state['document_id']}",
            extra={
                "narrative_length": len(state["generated_narrative"]),
                "elements": len(state["story_elements"]),
                "confidence": state["confidence_scores"].story_quality
            }
        )
        
        return state
    
    async def _generate_story_with_llm(
        self,
        entities: List[Any],
        facts: List[Dict[str, Any]],
        themes: List[str],
        context: str
    ) -> GeneratedStory:
        """Generate story using LLM"""
        # Prepare entity information
        entity_info = [
            f"{e.name} ({e.entity_type}): {e.context[:100]}..."
            for e in entities[:10]  # Limit to top 10 entities
        ]
        
        # Prepare fact information
        fact_info = [f["fact"] for f in facts[:15]]  # Limit to top 15 facts
        
        # Create chain
        chain = await self.create_llm_chain(
            self.story_prompt,
            self.story_parser
        )
        
        # Generate story
        story = await chain.ainvoke({
            "entities": "\n".join(entity_info),
            "facts": "\n".join(fact_info),
            "themes": ", ".join(themes),
            "context": context
        })
        
        return story
    
    def _generate_story_basic(
        self,
        entities: List[Any],
        facts: List[Dict[str, Any]],
        themes: List[str],
        doc_type: str
    ) -> str:
        """Generate basic story without LLM"""
        # Identify main characters (people and organizations)
        people = [e for e in entities if e.entity_type == "PERSON"]
        orgs = [e for e in entities if e.entity_type == "ORG"]
        
        # Start with introduction
        narrative_parts = []
        
        # Opening
        if people:
            main_character = people[0].name
            narrative_parts.append(
                f"This is the story of {main_character} and their involvement in "
                f"events that would shape {themes[0] if themes else 'important developments'}."
            )
        elif orgs:
            main_org = orgs[0].name
            narrative_parts.append(
                f"{main_org} found itself at the center of "
                f"{'a ' + self._get_narrative_type(doc_type)} story."
            )
        else:
            narrative_parts.append(
                f"This account explores {themes[0] if themes else 'significant events'} "
                f"through a series of interconnected developments."
            )
        
        # Add key facts as narrative elements
        if facts:
            narrative_parts.append("\n\nKey developments unfolded as follows:")
            for i, fact_dict in enumerate(facts[:5], 1):
                narrative_parts.append(f"\n{i}. {fact_dict['fact']}")
        
        # Add entities and their roles
        if entities:
            narrative_parts.append("\n\nCentral figures in this narrative include:")
            for entity in entities[:5]:
                narrative_parts.append(f"\n- {entity.name}: {entity.context[:100]}...")
        
        # Themes conclusion
        if themes:
            narrative_parts.append(
                f"\n\nThroughout these events, recurring themes of "
                f"{', '.join(themes[:3])} emerge, highlighting the complex nature "
                f"of the situation."
            )
        
        return " ".join(narrative_parts)
    
    def _get_narrative_type(self, doc_type: str) -> str:
        """Get narrative type based on document type"""
        narrative_map = {
            "report": "investigation",
            "interview": "biography",
            "article": "discovery",
            "research_paper": "discovery",
            "letter": "conflict"
        }
        
        narrative_type = narrative_map.get(doc_type, "transformation")
        return self.narrative_templates.get(narrative_type, "compelling")
    
    def _create_basic_story_elements(
        self,
        entities: List[Any],
        facts: List[Dict[str, Any]],
        themes: List[str]
    ) -> List[StoryElement]:
        """Create basic story elements without LLM"""
        elements = []
        
        # Character elements from entities
        for entity in entities[:5]:
            if entity.entity_type in ["PERSON", "ORG"]:
                elements.append(
                    StoryElement(
                        element_type="character",
                        content=f"{entity.name} - {entity.entity_type}",
                        source_reference=entity.context[:50],
                        confidence=0.7
                    )
                )
        
        # Plot elements from facts
        for fact_dict in facts[:5]:
            elements.append(
                StoryElement(
                    element_type="plot",
                    content=fact_dict["fact"],
                    source_reference=None,
                    confidence=0.6
                )
            )
        
        # Theme elements
        for theme in themes[:3]:
            elements.append(
                StoryElement(
                    element_type="theme",
                    content=f"Theme: {theme}",
                    source_reference=None,
                    confidence=0.5
                )
            )
        
        return elements