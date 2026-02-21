"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class ComponentModel(BaseModel):
    """Individual component model."""
    name: str
    type: str
    quantity: int
    notes: str
    extraction_index: int
    details: Optional[str] = ""
    player_specific: Optional[bool] = False
    player_identifier: Optional[str] = None


class ComponentGroupModel(BaseModel):
    """Component group model (V2 schema)."""
    group_name: str
    group_type: str
    per_player: bool
    identical_sets: Optional[bool] = False
    notes: str
    components: List[ComponentModel]


class ExtractionResponseData(BaseModel):
    """Extraction result data."""
    component_groups: List[ComponentGroupModel]
    game_name: str
    player_count: Dict[str, int]
    factions_or_colors: List[str]
    extraction_notes: str
    components: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ExtractionResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[ExtractionResponseData] = None
    error: Optional[str] = None
