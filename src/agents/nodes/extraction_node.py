"""
Entity and Information Extraction Node for STONESOUP LangGraph Workflow

This node extracts entities, facts, and themes from processed documents
using advanced NLP techniques and LLM-based analysis.
"""

from typing import List, Dict, Any, Optional, Set
import re
from collections import Counter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .base_node import BaseNode, NodeConfig
from ..state.agent_state import AgentState, ProcessingStage, ExtractedEntity


class ExtractionResult(BaseModel):
    """Model for extraction results from LLM"""
    entities: List[Dict[str, Any]] = Field(description="Extracted entities with types and context")
    facts: List[str] = Field(description="Key facts extracted from the content")
    themes: List[str] = Field(description="Main themes and topics")
    relationships: List[Dict[str, str]] = Field(description="Relationships between entities")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")


class ExtractionNode(BaseNode):
    """
    Node responsible for extracting structured information from documents.
    
    Key responsibilities:
    - Extract named entities (people, places, organizations, etc.)
    - Identify key facts and claims
    - Discover themes and topics
    - Map relationships between entities
    """
    
    def __init__(self, config: Optional[NodeConfig] = None, **kwargs):
        """Initialize extraction node with default config if not provided"""
        if not config:
            config = NodeConfig(
                name="extraction_node",
                description="Entity and information extraction",
                max_retries=3,
                timeout_seconds=180,
                required_confidence=0.7
            )
        super().__init__(config, **kwargs)
        
        # Entity extraction prompt
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert information extraction specialist. Extract the following from the provided text:

            1. ENTITIES: Identify all named entities with their types:
               - People (PERSON): Full names, titles, roles
               - Organizations (ORG): Companies, institutions, groups
               - Locations (LOC): Cities, countries, addresses
               - Events (EVENT): Conferences, incidents, meetings
               - Dates/Times (TIME): Specific dates, time periods
               - Other relevant entities
            
            2. FACTS: Extract key facts, claims, and statements that are:
               - Specific and verifiable
               - Important to the document's purpose
               - Supported by evidence in the text
            
            3. THEMES: Identify 3-5 main themes or topics discussed
            
            4. RELATIONSHIPS: Note important relationships between entities
               (e.g., "John Smith" -> "works for" -> "Acme Corp")
            
            Provide your confidence level (0-1) in the extraction quality."""),
            ("human", "Text to analyze:\n\n{content}\n\nExtract entities, facts, themes, and relationships.")
        ])
        
        self.extraction_parser = PydanticOutputParser(pydantic_object=ExtractionResult)
        
        # Entity type mapping
        self.entity_types = {
            "PERSON": ["person", "people", "individual", "human"],
            "ORG": ["organization", "company", "corporation", "institution", "agency"],
            "LOC": ["location", "place", "city", "country", "address", "region"],
            "EVENT": ["event", "incident", "conference", "meeting", "occurrence"],
            "TIME": ["date", "time", "period", "year", "month", "day"],
            "PRODUCT": ["product", "service", "software", "technology"],
            "CONCEPT": ["concept", "idea", "theory", "principle"]
        }
    
    def _validate_input(self, state: AgentState) -> List[str]:
        """Validate input state for extraction"""
        errors = []
        
        if not state.get("processed_content"):
            errors.append("No processed content available")
        
        if state["current_stage"] != ProcessingStage.EXTRACTION:
            errors.append(f"Invalid stage for extraction: {state['current_stage']}")
        
        return errors
    
    async def _process(self, state: AgentState) -> AgentState:
        """
        Extract entities and information from processed content.
        
        Steps:
        1. Extract entities using NER
        2. Identify key facts and claims
        3. Discover themes and topics
        4. Map entity relationships
        """
        self.logger.info(f"Starting extraction for document {state['document_id']}")
        
        content = state["processed_content"]
        sections = self.get_context(state, "document_sections", [])
        
        # Process each section if available, otherwise process full content
        if sections and self.llm:
            # Extract from each section and aggregate
            all_entities = []
            all_facts = []
            all_themes = []
            
            for section in sections[:5]:  # Limit to first 5 sections for performance
                section_result = await self._extract_from_section(
                    section["content"],
                    section["title"]
                )
                
                # Aggregate results
                all_entities.extend(section_result["entities"])
                all_facts.extend(section_result["facts"])
                all_themes.extend(section_result["themes"])
            
            # Deduplicate and process
            entities = self._deduplicate_entities(all_entities)
            facts = self._deduplicate_facts(all_facts)
            themes = self._identify_top_themes(all_themes)
            
        else:
            # Extract from full content
            if self.llm:
                extraction_result = await self._extract_with_llm(content)
                entities = extraction_result.entities
                facts = extraction_result.facts
                themes = extraction_result.themes
                state["confidence_scores"].extraction = extraction_result.confidence
            else:
                # Fallback to basic extraction
                entities = self._extract_entities_basic(content)
                facts = self._extract_facts_basic(content)
                themes = self._extract_themes_basic(content)
                state["confidence_scores"].extraction = 0.6
        
        # Convert to ExtractedEntity objects
        state["extracted_entities"] = [
            self._create_entity_object(entity, content)
            for entity in entities
        ]
        
        # Store facts and themes
        state["extracted_facts"] = [{"fact": fact, "confidence": 0.8} for fact in facts]
        state["key_themes"] = themes
        
        # Update confidence score
        state["confidence_scores"].update_overall()
        
        # Add extraction summary to context
        self.add_context(state, "entity_count", len(state["extracted_entities"]))
        self.add_context(state, "fact_count", len(state["extracted_facts"]))
        self.add_context(state, "theme_count", len(state["key_themes"]))
        
        # Update stage
        self.update_stage(state, ProcessingStage.STORY_GENERATION)
        
        self.logger.info(
            f"Extraction complete for {state['document_id']}",
            extra={
                "entities": len(state["extracted_entities"]),
                "facts": len(state["extracted_facts"]),
                "themes": len(state["key_themes"]),
                "confidence": state["confidence_scores"].extraction
            }
        )
        
        return state
    
    async def _extract_from_section(
        self,
        content: str,
        section_title: str
    ) -> Dict[str, Any]:
        """Extract information from a single section"""
        try:
            chain = await self.create_llm_chain(
                self.extraction_prompt,
                self.extraction_parser
            )
            
            result = await chain.ainvoke({"content": content})
            
            # Add section context to entities
            for entity in result.entities:
                entity["section"] = section_title
            
            return {
                "entities": result.entities,
                "facts": result.facts,
                "themes": result.themes
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to extract from section {section_title}: {e}")
            return {"entities": [], "facts": [], "themes": []}
    
    async def _extract_with_llm(self, content: str) -> ExtractionResult:
        """Extract information using LLM"""
        # Truncate content if too long
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        chain = await self.create_llm_chain(
            self.extraction_prompt,
            self.extraction_parser
        )
        
        return await chain.ainvoke({"content": content})
    
    def _extract_entities_basic(self, content: str) -> List[Dict[str, Any]]:
        """Basic entity extraction without LLM"""
        entities = []
        
        # Simple patterns for common entity types
        patterns = {
            "PERSON": r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b',
            "ORG": r'\b[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*(?:\sInc\.?|\sCorp\.?|\sLLC|\sLtd\.?)\b',
            "LOC": r'\b(?:New York|London|Paris|Tokyo|[A-Z][a-z]+(?:,\s*[A-Z]{2})?)\b',
            "TIME": r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}|January|February|March|April|May|June|July|August|September|October|November|December)\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                entities.append({
                    "type": entity_type,
                    "name": match.group(),
                    "context": content[max(0, match.start()-50):match.end()+50]
                })
        
        return entities
    
    def _extract_facts_basic(self, content: str) -> List[str]:
        """Basic fact extraction without LLM"""
        facts = []
        
        # Look for sentences with fact indicators
        sentences = content.split('.')
        fact_indicators = ['reported', 'announced', 'discovered', 'found', 'revealed', 'stated']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in fact_indicators):
                if len(sentence) > 20 and len(sentence) < 200:
                    facts.append(sentence + '.')
        
        return facts[:10]  # Limit to top 10 facts
    
    def _extract_themes_basic(self, content: str) -> List[str]:
        """Basic theme extraction without LLM"""
        # Simple word frequency analysis
        words = re.findall(r'\b[a-z]+\b', content.lower())
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        words = [w for w in words if w not in stop_words and len(w) > 4]
        
        # Get most common words as themes
        word_freq = Counter(words)
        themes = [word for word, _ in word_freq.most_common(5)]
        
        return themes
    
    def _create_entity_object(
        self,
        entity_data: Dict[str, Any],
        full_content: str
    ) -> ExtractedEntity:
        """Create ExtractedEntity object from raw entity data"""
        # Normalize entity type
        entity_type = entity_data.get("type", "UNKNOWN").upper()
        
        # Find better context if needed
        name = entity_data.get("name", "")
        context = entity_data.get("context", "")
        
        if not context and name:
            # Find entity in content
            index = full_content.find(name)
            if index != -1:
                start = max(0, index - 100)
                end = min(len(full_content), index + len(name) + 100)
                context = full_content[start:end]
        
        return ExtractedEntity(
            entity_type=entity_type,
            name=name,
            context=context,
            confidence=entity_data.get("confidence", 0.7),
            metadata=entity_data
        )
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.get("type", ""), entity.get("name", "").lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _deduplicate_facts(self, facts: List[str]) -> List[str]:
        """Remove duplicate or similar facts"""
        unique_facts = []
        seen_facts = set()
        
        for fact in facts:
            # Simple similarity check (could be enhanced)
            fact_lower = fact.lower().strip()
            if fact_lower not in seen_facts:
                seen_facts.add(fact_lower)
                unique_facts.append(fact)
        
        return unique_facts
    
    def _identify_top_themes(self, all_themes: List[str]) -> List[str]:
        """Identify top themes from all extracted themes"""
        theme_counter = Counter(all_themes)
        
        # Get top 5 themes
        top_themes = [theme for theme, _ in theme_counter.most_common(5)]
        
        return top_themes