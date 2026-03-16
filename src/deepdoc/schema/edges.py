"""Relationship types for the code knowledge graph."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EdgeType(str, Enum):
    # Module wiring
    IMPORTS_MODULE = "imports_module"
    REGISTERS_IN_ROUTER = "registers_in_router"
    EXPORTS_MODULE = "exports_module"

    # Dependency injection
    PROVIDES = "provides"
    INJECTS = "injects"
    USES_GUARD = "uses_guard"
    USES_DECORATOR = "uses_decorator"

    # TypeORM / Database
    CONNECTS_TO_DB = "connects_to_db"
    REGISTERS_ENTITY = "registers_entity"
    HAS_RELATION = "has_relation"

    # Code structure
    IMPORTS_SYMBOL = "imports_symbol"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    CALLS = "calls"
    DEFINES_ROUTE = "defines_route"

    # Business logic
    VALIDATES_WITH = "validates_with"
    QUEUES_JOB = "queues_job"
    HANDLES_JOB = "handles_job"


class CodeRelationship(BaseModel):
    """An edge in the code knowledge graph."""

    edge_type: EdgeType = Field(description="Relationship type")
    source_file: str = Field(description="File where this relationship is defined")
    source_function: Optional[str] = Field(
        None, description="Function/method where this relationship is defined"
    )
    evidence_snippet: str = Field(
        "", description="Code snippet proving this relationship"
    )
