"""
Data models for bundle management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


@dataclass
class BundleInfo:
    """Complete information about a bundle."""
    bundle_id: str
    description: str
    sources: List[str]
    default_count: int
    total_sources: int
    category_distribution: Dict[str, int]


@dataclass
class BundleData:
    """Data for creating/updating a bundle."""
    bundle_id: str
    description: str
    default_count: int = 20
    sources: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    valid: bool
    errors: List[str]
    warnings: List[str] = field(default_factory=list)


@dataclass
class BackupMetadata:
    """Metadata for bundle backup."""
    backup_id: str
    timestamp: datetime
    file_path: Path
    bundle_count: int
    bundles: List[str]  # List of bundle IDs in backup

    @property
    def formatted_timestamp(self) -> str:
        """Human-readable timestamp."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class BundleOperation:
    """Record of bundle operation for undo/audit."""
    operation_type: str  # create, delete, update, add_sources, remove_sources
    bundle_id: str
    timestamp: datetime
    details: Dict[str, Any]
    backup_id: Optional[str] = None
