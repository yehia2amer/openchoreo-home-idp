"""Platform profile layer — resolves a platform name into a typed capability profile."""

from platforms.resolver import resolve_platform
from platforms.types import PlatformProfile

__all__ = ["PlatformProfile", "resolve_platform"]
