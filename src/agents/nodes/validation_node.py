"""
Validation Node for STONESOUP LangGraph Workflow

This node validates generated content for quality, accuracy, and completeness,
providing scoring and feedback for improvement.
"""

from typing import List, Dict, Any, Optional, Set
import re
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .base_node import BaseNode, NodeConfig
from ..state.agent_state import AgentState, ProcessingStage, ValidationResult


class ValidationChecks(BaseModel):
    """Model for detailed validation checks"""
    factual_accuracy: float = Field(ge=0.0, le=1.0, description="Factual accuracy score")
    narrative_coherence: float = Field(ge=0.0, le=1.0, description="Narrative coherence score")
    completeness: float = Field(ge=0.0, le=1.0, description="Content completeness score")
    clarity: float = Field(ge=0.0, le=1.0, description="Clarity and readability score")
    entity_coverage: float = Field(ge=0.0, le=1.0, description="Entity coverage score")
    theme_integration: float = Field(ge=0.0, le=1.0, description="Theme integration score")
    errors: List[str] = Field(default_factory=list, description="List of errors found")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Overall validation confidence")


class ValidationNode(BaseNode):
    """
    Node responsible for validating and scoring generated content.
    
    Key responsibilities:
    - Check factual accuracy against extracted information
    - Assess narrative quality and coherence
    - Verify entity and theme coverage
    - Provide actionable feedback for improvement
    - Generate final quality scores
    """
    
    def __init__(self, config: Optional[NodeConfig] = None, **kwargs):
        """Initialize validation node with default config if not provided"""
        if not config:
            config = NodeConfig(
                name="validation_node",
                description="Content validation and quality scoring",
                max_retries=2,
                timeout_seconds=120,
                required_confidence=0.8
            )
        super().__init__(config, **kwargs)
        
        # Validation prompt
        self.validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meticulous content validator and quality assessor. Evaluate the generated narrative against the source information.

            Perform these validation checks:
            
            1. FACTUAL ACCURACY (0-1):
               - Are all facts in the narrative supported by the source data?
               - Are entities correctly represented?
               - Is chronology accurate?
            
            2. NARRATIVE COHERENCE (0-1):
               - Does the story flow logically?
               - Are transitions smooth?
               - Is the narrative structure clear?
            
            3. COMPLETENESS (0-1):
               - Are all key entities included?
               - Are important facts covered?
               - Are themes adequately explored?
            
            4. CLARITY (0-1):
               - Is the language clear and accessible?
               - Are complex ideas well-explained?
               - Is the reading level appropriate?
            
            5. ENTITY COVERAGE (0-1):
               - What percentage of entities are included?
               - Are they properly contextualized?
            
            6. THEME INTEGRATION (0-1):
               - Are themes woven throughout?
               - Do they enhance the narrative?
            
            Identify:
            - ERRORS: Factual inaccuracies, misrepresentations
            - WARNINGS: Potential issues, unclear passages
            - SUGGESTIONS: Specific improvements
            
            Provide an overall confidence score for the content quality."""),
            ("human", """Source Entities: {entities}
            
            Source Facts: {facts}
            
            Themes: {themes}
            
            Generated Narrative:
            {narrative}
            
            Validate this narrative against the source information.""")
        ])
        
        self.validation_parser = PydanticOutputParser(pydantic_object=ValidationChecks)
        
        # Validation thresholds
        self.thresholds = {
            "minimum_score": 0.6,
            "good_score": 0.8,
            "excellent_score": 0.9
        }
    
    def _validate_input(self, state: AgentState) -> List[str]:
        """Validate input state for validation"""
        errors = []
        
        if state["current_stage"] != ProcessingStage.VALIDATION:
            errors.append(f"Invalid stage for validation: {state['current_stage']}")
        
        if not state.get("generated_narrative"):
            errors.append("No generated narrative to validate")
        
        return errors
    
    async def _process(self, state: AgentState) -> AgentState:
        """
        Validate generated content.
        
        Steps:
        1. Check factual accuracy
        2. Assess narrative quality
        3. Verify completeness
        4. Generate scores and feedback
        """
        self.logger.info(f"Starting validation for document {state['document_id']}")
        
        narrative = state["generated_narrative"]
        entities = state["extracted_entities"]
        facts = state["extracted_facts"]
        themes = state["key_themes"]
        
        if self.llm:
            # Perform LLM-based validation
            validation_checks = await self._validate_with_llm(
                narrative, entities, facts, themes
            )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(validation_checks)
            
            # Create validation result
            validation_result = ValidationResult(
                is_valid=overall_score >= self.thresholds["minimum_score"],
                errors=validation_checks.errors,
                warnings=validation_checks.warnings,
                suggestions=validation_checks.suggestions,
                score=overall_score
            )
            
            # Update confidence
            state["confidence_scores"].validation = validation_checks.overall_confidence
            
        else:
            # Perform basic validation
            validation_result = self._validate_basic(
                narrative, entities, facts, themes
            )
            state["confidence_scores"].validation = 0.7
        
        # Store validation result
        state["validation_result"] = validation_result
        
        # Update overall confidence
        state["confidence_scores"].update_overall()
        
        # Add validation details to context
        self.add_context(state, "validation_score", validation_result.score)
        self.add_context(state, "error_count", len(validation_result.errors))
        self.add_context(state, "warning_count", len(validation_result.warnings))
        
        # Determine final stage based on validation
        if validation_result.is_valid:
            self.update_stage(state, ProcessingStage.COMPLETED)
            self.logger.info(
                f"Validation passed for {state['document_id']}",
                extra={"score": validation_result.score}
            )
        else:
            # Check if we should retry
            if state["retry_count"] < state["max_retries"] and validation_result.score > 0.4:
                state["should_retry"] = True
                self.update_stage(state, ProcessingStage.STORY_GENERATION)
                self.logger.warning(
                    f"Validation failed, retrying for {state['document_id']}",
                    extra={"score": validation_result.score, "retry": state["retry_count"] + 1}
                )
            else:
                self.update_stage(state, ProcessingStage.FAILED)
                self.logger.error(
                    f"Validation failed for {state['document_id']}",
                    extra={"score": validation_result.score}
                )
        
        return state
    
    async def _validate_with_llm(
        self,
        narrative: str,
        entities: List[Any],
        facts: List[Dict[str, Any]],
        themes: List[str]
    ) -> ValidationChecks:
        """Validate using LLM"""
        # Prepare entity information
        entity_info = [
            f"{e.name} ({e.entity_type})"
            for e in entities[:20]  # Limit for context window
        ]
        
        # Prepare fact information
        fact_info = [f["fact"] for f in facts[:20]]
        
        # Create chain
        chain = await self.create_llm_chain(
            self.validation_prompt,
            self.validation_parser
        )
        
        # Validate
        validation = await chain.ainvoke({
            "entities": "\n".join(entity_info),
            "facts": "\n".join(fact_info),
            "themes": ", ".join(themes),
            "narrative": narrative[:5000]  # Limit narrative length
        })
        
        return validation
    
    def _validate_basic(
        self,
        narrative: str,
        entities: List[Any],
        facts: List[Dict[str, Any]],
        themes: List[str]
    ) -> ValidationResult:
        """Perform basic validation without LLM"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check entity coverage
        entity_names = {e.name.lower() for e in entities}
        narrative_lower = narrative.lower()
        
        covered_entities = sum(
            1 for name in entity_names
            if name in narrative_lower
        )
        
        entity_coverage = covered_entities / len(entity_names) if entity_names else 0
        
        if entity_coverage < 0.5:
            warnings.append(f"Low entity coverage: {entity_coverage:.1%}")
            suggestions.append("Include more entities from the source material")
        
        # Check fact coverage
        covered_facts = sum(
            1 for fact_dict in facts
            if any(word in narrative_lower for word in fact_dict["fact"].lower().split()[:5])
        )
        
        fact_coverage = covered_facts / len(facts) if facts else 0
        
        if fact_coverage < 0.3:
            warnings.append(f"Low fact coverage: {fact_coverage:.1%}")
            suggestions.append("Incorporate more facts from the source")
        
        # Check narrative length
        word_count = len(narrative.split())
        if word_count < 100:
            errors.append("Narrative too short (less than 100 words)")
        elif word_count < 200:
            warnings.append("Narrative may be too brief")
        
        # Check theme integration
        theme_mentions = sum(
            1 for theme in themes
            if theme.lower() in narrative_lower
        )
        
        theme_coverage = theme_mentions / len(themes) if themes else 0
        
        if theme_coverage < 0.5:
            suggestions.append("Better integrate identified themes into the narrative")
        
        # Calculate overall score
        score = (entity_coverage * 0.3 + fact_coverage * 0.3 + theme_coverage * 0.2 + 0.2)
        
        # Adjust score based on errors/warnings
        score -= len(errors) * 0.1
        score -= len(warnings) * 0.05
        score = max(0.0, min(1.0, score))
        
        return ValidationResult(
            is_valid=score >= 0.6 and len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            score=score
        )
    
    def _calculate_overall_score(self, checks: ValidationChecks) -> float:
        """Calculate overall validation score from individual checks"""
        # Weighted average of different aspects
        weights = {
            "factual_accuracy": 0.3,
            "narrative_coherence": 0.2,
            "completeness": 0.2,
            "clarity": 0.1,
            "entity_coverage": 0.1,
            "theme_integration": 0.1
        }
        
        score = sum(
            getattr(checks, aspect) * weight
            for aspect, weight in weights.items()
        )
        
        # Penalize for errors and warnings
        error_penalty = len(checks.errors) * 0.1
        warning_penalty = len(checks.warnings) * 0.05
        
        final_score = max(0.0, min(1.0, score - error_penalty - warning_penalty))
        
        return final_score