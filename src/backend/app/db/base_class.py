"""
Base model class with common fields for all database models.

This module provides a declarative base class that includes common fields
used across all models in the STONESOUP application:
- UUID primary key for distributed systems compatibility
- Timestamps for audit trails
- Multi-tenancy support through cauldron_id

The design follows these principles:
1. UUID primary keys for better distributed system support and security
2. Automatic timestamp management for audit trails
3. Multi-tenancy at the database level for data isolation
4. Consistent field naming across all models
"""
from typing import Any
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
import uuid


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models in STONESOUP.
    
    Provides common fields and functionality:
    - id: UUID primary key for better distributed system support
    - created_at/updated_at: Automatic timestamp management
    - cauldron_id: Multi-tenancy support at the database level
    
    All models inheriting from this base will automatically have these fields,
    ensuring consistency across the application and enabling features like
    audit trails and data isolation per organization (cauldron).
    """
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name.
        Converts CamelCase to snake_case and pluralizes.
        """
        import re
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Simple pluralization (add 's' unless it ends in 'y')
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith('s'):
            return name + 'es'
        else:
            return name + 's'


class TimestampMixin:
    """
    Mixin that provides timestamp fields for models.
    
    Automatically manages created_at and updated_at timestamps,
    ensuring all models have consistent audit trail capabilities.
    """
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when the record was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when the record was last updated"
    )


class CauldronMixin:
    """
    Mixin that provides multi-tenancy support through cauldron_id.
    
    This enables data isolation at the database level, ensuring that
    each organization's (cauldron's) data is kept separate. The foreign
    key relationship ensures referential integrity.
    """
    @declared_attr
    def cauldron_id(cls):
        """
        Foreign key to the cauldron (organization/workspace) this record belongs to.
        
        This field enables multi-tenancy at the database level, ensuring
        data isolation between different organizations using the platform.
        """
        return Column(
            UUID(as_uuid=True),
            ForeignKey('cauldrons.id', ondelete='CASCADE'),
            nullable=False,
            index=True,
            comment="ID of the cauldron (organization) this record belongs to"
        )
    
    @declared_attr
    def cauldron(cls):
        """Relationship to the Cauldron model."""
        return relationship("Cauldron", back_populates=cls.__tablename__)


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model with common fields for all database models.
    
    Combines the declarative base with timestamp functionality,
    providing a foundation for all models in the application.
    Models that need multi-tenancy should also inherit from CauldronMixin.
    """
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the record"
    )
    
    def __repr__(self) -> str:
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        
        Base implementation that can be overridden by specific models
        to include additional fields or exclude sensitive data.
        """
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }