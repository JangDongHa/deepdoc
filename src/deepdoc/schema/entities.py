"""Entity types for the code knowledge graph."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    MODULE = "Module"
    CONTROLLER = "Controller"
    SERVICE = "Service"
    REPOSITORY = "Repository"
    GUARD = "Guard"
    DECORATOR = "Decorator"
    ENTITY = "Entity"
    DTO = "DTO"
    SPEC = "Spec"
    CONFIG = "Config"
    ROUTE_PREFIX = "RoutePrefix"
    QUEUE = "Queue"
    DATABASE_CONNECTION = "DatabaseConnection"
    EXTERNAL_PACKAGE = "ExternalPackage"
    FUNCTION = "Function"
    MIDDLEWARE = "Middleware"
    INTERCEPTOR = "Interceptor"
    FILTER = "Filter"
    PIPE = "Pipe"


class CodeEntity(BaseModel):
    """A node in the code knowledge graph."""

    name: str = Field(description="Entity name (e.g. class name, file name)")
    entity_type: EntityType = Field(description="Type classification")
    file_path: str = Field(description="Absolute path to source file")
    function_name: Optional[str] = Field(
        None, description="Function/method name for sub-file precision"
    )
    export_name: Optional[str] = Field(
        None, description="Exported symbol name"
    )
    description: str = Field("", description="Brief description")
