"""
Core application modules for Ally Platform.

This module contains the core configuration and utility functions
used throughout the Ally Platform backend.
"""

# Import commonly used functions for easier access
from .config import (
    load_config,
    get_config_value,
    is_feature_enabled,
    get_company_name,
    reload_config,
)

__all__ = [
    "load_config",
    "get_config_value",
    "is_feature_enabled",
    "get_company_name",
    "reload_config",
]
