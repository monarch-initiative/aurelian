"""Simple output models for Knowledge Agent - dynamic based on schema."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class SimpleEntity(BaseModel):
    """General entity that adapts to any schema."""
    text: str = Field(..., description="Original text mention")
    entity_type: str = Field(..., description="Type from schema (gene, house, fish, etc.)")
    ontology_id: Optional[str] = Field(None, description="Grounded ontology ID if available")
    ontology_label: Optional[str] = Field(None, description="Ontology term label")
    is_grounded: bool = Field(default=False, description="Whether entity was successfully grounded to ontology")
    match_type: Optional[str] = Field(None, description="Type of match: 'label', 'synonym', or 'none'")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    grounding_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Ontology grounding confidence")
    grounding_source: Optional[str] = Field(None, description="Source of grounding: 'ontology:mondo', 'ontology:hgnc', 'web_search', etc.")
    curator_note: Optional[str] = Field(None, description="Note for curators about grounding quality")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties from schema")


class SimpleRelationship(BaseModel):
    """Simple relationship between entities."""
    subject: str = Field(..., description="Subject entity text")
    predicate: str = Field(..., description="Relationship type from schema")
    object: str = Field(..., description="Object entity text")


class MissingEntity(BaseModel):
    """Entity that was likely present in text but not extracted."""
    text: str = Field(..., description="Text that might contain an entity")
    suggested_type: str = Field(..., description="Suggested entity type")
    reason: str = Field(..., description="Why this might have been missed")


class ExtractionResult(BaseModel):
    """Simple extraction result in JSON format."""
    entities: List[SimpleEntity] = Field(default_factory=list)
    relationships: List[SimpleRelationship] = Field(default_factory=list)
    potentially_missing: List[MissingEntity] = Field(default_factory=list, description="Entities that might have been missed")
    schema_name: Optional[str] = Field(None, description="Schema used for extraction")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to simple JSON dictionary."""
        return {
            "entities": [entity.model_dump() for entity in self.entities],
            "relationships": [rel.model_dump() for rel in self.relationships],
            "potentially_missing": [missing.model_dump() for missing in self.potentially_missing],
            "schema_name": self.schema_name,
            "timestamp": self.timestamp.isoformat()
        }


# Simple union for different output modes
KnowledgeAgentOutput = Union[ExtractionResult, str]