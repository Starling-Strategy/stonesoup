"""
Document Ingestion Node for STONESOUP LangGraph Workflow

This node handles the initial processing of raw documents,
including parsing, cleaning, and preparing content for downstream processing.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .base_node import BaseNode, NodeConfig
from ..state.agent_state import AgentState, ProcessingStage


class DocumentAnalysis(BaseModel):
    """Model for document analysis results"""
    document_type: str = Field(description="Type of document (report, article, transcript, etc)")
    language: str = Field(description="Primary language of the document")
    summary: str = Field(description="Brief summary of document content")
    key_sections: List[str] = Field(description="Main sections identified in the document")
    quality_score: float = Field(ge=0.0, le=1.0, description="Document quality score")
    confidence: float = Field(ge=0.0, le=1.0, description="Analysis confidence")


class IngestionNode(BaseNode):
    """
    Node responsible for ingesting and preprocessing raw documents.
    
    Key responsibilities:
    - Clean and normalize text content
    - Detect document structure and type
    - Extract basic metadata
    - Prepare content for entity extraction
    """
    
    def __init__(self, config: Optional[NodeConfig] = None, **kwargs):
        """Initialize ingestion node with default config if not provided"""
        if not config:
            config = NodeConfig(
                name="ingestion_node",
                description="Document ingestion and preprocessing",
                max_retries=3,
                timeout_seconds=120,
                required_confidence=0.6
            )
        super().__init__(config, **kwargs)
        
        # Analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document analysis expert. Analyze the provided document and extract:
            1. Document type (report, article, transcript, interview, etc)
            2. Primary language
            3. Brief summary (2-3 sentences)
            4. Main sections or topics covered
            5. Quality assessment (0-1 score based on clarity, structure, completeness)
            
            Provide your confidence level (0-1) in this analysis."""),
            ("human", "Document content:\n\n{content}\n\nAnalyze this document.")
        ])
        
        self.analysis_parser = PydanticOutputParser(pydantic_object=DocumentAnalysis)
    
    def _validate_input(self, state: AgentState) -> List[str]:
        """Validate input state for ingestion"""
        errors = []
        
        if not state.get("raw_content"):
            errors.append("No raw content provided")
        
        if not state.get("document_id"):
            errors.append("No document ID provided")
        
        if state["current_stage"] != ProcessingStage.INGESTION:
            errors.append(f"Invalid stage for ingestion: {state['current_stage']}")
        
        return errors
    
    async def _process(self, state: AgentState) -> AgentState:
        """
        Process raw document content.
        
        Steps:
        1. Clean and normalize text
        2. Detect structure and metadata
        3. Analyze document quality
        4. Prepare for extraction
        """
        self.logger.info(f"Processing document {state['document_id']}")
        
        # Clean and normalize content
        cleaned_content = self._clean_text(state["raw_content"])
        state["processed_content"] = cleaned_content
        
        # Update metadata
        state["metadata"].word_count = len(cleaned_content.split())
        state["metadata"].ingestion_timestamp = datetime.utcnow()
        
        # Analyze document if LLM is available
        if self.llm:
            analysis = await self._analyze_document(cleaned_content)
            
            # Update metadata with analysis results
            state["metadata"].document_type = analysis.document_type
            state["metadata"].language = analysis.language
            
            # Add document summary to context
            self.add_context(state, "document_summary", analysis.summary)
            self.add_context(state, "key_sections", analysis.key_sections)
            
            # Update confidence
            state["confidence_scores"].overall = analysis.confidence
            
            # Log quality assessment
            if analysis.quality_score < 0.5:
                state["error_messages"].append(
                    f"Low document quality detected: {analysis.quality_score:.2f}"
                )
        else:
            # Basic analysis without LLM
            state["metadata"].document_type = self._detect_document_type(cleaned_content)
            state["metadata"].language = "en"  # Default to English
            state["confidence_scores"].overall = 0.7
        
        # Prepare sections for extraction
        sections = self._segment_document(cleaned_content)
        self.add_context(state, "document_sections", sections)
        
        # Update stage for next node
        self.update_stage(state, ProcessingStage.EXTRACTION)
        
        self.logger.info(
            f"Ingestion complete for {state['document_id']}",
            extra={
                "word_count": state["metadata"].word_count,
                "document_type": state["metadata"].document_type,
                "confidence": state["confidence_scores"].overall
            }
        )
        
        return state
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize raw text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special Unicode characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?;:()\'"]+', '', text)
        
        # Fix common OCR errors
        text = self._fix_common_ocr_errors(text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in text"""
        replacements = {
            r'\bl\s+l\b': 'll',  # l l -> ll
            r'\bi\s+n\b': 'in',   # i n -> in
            r'\bt\s+h\s+e\b': 'the',  # t h e -> the
            r'\ba\s+n\s+d\b': 'and',  # a n d -> and
            r'(?<=[a-z])(?=[A-Z])': ' ',  # Add space between camelCase
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _detect_document_type(self, content: str) -> str:
        """
        Detect document type based on content patterns.
        
        Args:
            content: Document content
            
        Returns:
            Detected document type
        """
        content_lower = content.lower()
        
        # Check for common document type indicators
        if re.search(r'(interview|q\s*:\s*|a\s*:\s*)', content_lower):
            return "interview"
        elif re.search(r'(chapter|section\s+\d+|table of contents)', content_lower):
            return "book"
        elif re.search(r'(abstract|methodology|conclusion|references)', content_lower):
            return "research_paper"
        elif re.search(r'(dear|sincerely|regards)', content_lower):
            return "letter"
        elif re.search(r'(executive summary|findings|recommendations)', content_lower):
            return "report"
        else:
            return "article"
    
    def _segment_document(self, content: str) -> List[Dict[str, str]]:
        """
        Segment document into logical sections.
        
        Args:
            content: Document content
            
        Returns:
            List of document sections
        """
        sections = []
        
        # Try to identify section headers
        header_pattern = r'\n\s*([A-Z][A-Z\s]+)\s*\n'
        matches = list(re.finditer(header_pattern, content))
        
        if matches:
            # Document has clear sections
            for i, match in enumerate(matches):
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                
                section = {
                    "title": match.group(1).strip(),
                    "content": content[start:end].strip(),
                    "position": i
                }
                sections.append(section)
        else:
            # No clear sections, split by paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # Group into logical sections (e.g., 5 paragraphs per section)
            for i in range(0, len(paragraphs), 5):
                section = {
                    "title": f"Section {i // 5 + 1}",
                    "content": '\n\n'.join(paragraphs[i:i+5]),
                    "position": i // 5
                }
                sections.append(section)
        
        return sections
    
    async def _analyze_document(self, content: str) -> DocumentAnalysis:
        """
        Analyze document using LLM.
        
        Args:
            content: Document content
            
        Returns:
            Document analysis results
        """
        # Truncate content if too long (keep first and last parts)
        max_length = 3000
        if len(content) > max_length:
            truncated = content[:max_length//2] + "\n...\n" + content[-max_length//2:]
        else:
            truncated = content
        
        # Create and run chain
        chain = await self.create_llm_chain(
            self.analysis_prompt,
            self.analysis_parser
        )
        
        analysis = await chain.ainvoke({"content": truncated})
        
        return analysis