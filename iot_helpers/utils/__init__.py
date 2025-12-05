"""
Utility Functions Module

Provides utility functions for naming conventions, resource tagging,
and dependency management.
"""

from .naming_conventions import (
    generate_thing_name,
    validate_thing_prefix,
    matches_workshop_pattern,
    NAMING_PATTERNS
)
from .resource_tagger import apply_workshop_tags, WORKSHOP_TAGS
from .dependency_handler import DependencyHandler, DELETION_ORDER

__all__ = [
    'generate_thing_name',
    'validate_thing_prefix', 
    'matches_workshop_pattern',
    'NAMING_PATTERNS',
    'apply_workshop_tags',
    'WORKSHOP_TAGS',
    'DependencyHandler',
    'DELETION_ORDER'
]
