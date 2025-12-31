# Implementation Plan: Bundle Management System
**Version:** 1.0
**Date:** October 24, 2025
**Based on:** PRD-Bundle-Management-System.md
**Estimated Duration:** 4 weeks (80-100 hours)

---

## Executive Summary

Four-phase implementation of comprehensive bundle management system:
1. **Phase 1:** Core CRUD operations (20-25 hours)
2. **Phase 2:** Source management operations (25-30 hours)
3. **Phase 3:** UI integration (20-25 hours)
4. **Phase 4:** Safety features and polish (15-20 hours)

Each phase delivers working, tested functionality. Phases can be deployed incrementally.

---

## Phase 1: Core CRUD Operations
**Duration:** 5-7 days (20-25 hours)
**Goal:** Extend BundleManager with complete CRUD operations

### 1.1 Extend BundleManager Class

**File:** `core/source_system/bundle_manager.py`
**Lines to Add:** ~200 lines

**New Methods:**

```python
def create_bundle(
    self,
    bundle_id: str,
    description: str,
    default_count: int = 20,
    sources: List[str] = None
) -> None:
    """
    Create new bundle in bundles.yml.

    Args:
        bundle_id: Unique bundle identifier (lowercase_with_underscores)
        description: Bundle description (1-200 chars)
        default_count: Default article count (1-100, default 20)
        sources: Initial source list (optional, default [])

    Raises:
        ValueError: If bundle_id exists or invalid
    """
    if bundle_id in self.data.get('bundles', {}):
        raise ValueError(f"Bundle '{bundle_id}' already exists")

    if sources is None:
        sources = []

    bundles = self.data.setdefault('bundles', {})
    bundles[bundle_id] = {
        'description': description,
        'sources': sources,
        'default_count': default_count
    }
    self._save_data()


def delete_bundle(self, bundle_id: str) -> None:
    """
    Delete bundle from bundles.yml.

    Args:
        bundle_id: Bundle to delete

    Raises:
        ValueError: If bundle not found or protected
    """
    if bundle_id == 'all':
        raise ValueError("Cannot delete 'all' bundle (system bundle)")

    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    del bundles[bundle_id]
    self._save_data()


def update_bundle_metadata(
    self,
    bundle_id: str,
    description: str = None,
    default_count: int = None
) -> None:
    """
    Update bundle metadata (description and/or default_count).

    Args:
        bundle_id: Bundle to update
        description: New description (optional)
        default_count: New default count (optional)

    Raises:
        ValueError: If bundle not found or no changes provided
    """
    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    if description is None and default_count is None:
        raise ValueError("Must provide at least one field to update")

    bundle = bundles[bundle_id]
    if description is not None:
        bundle['description'] = description
    if default_count is not None:
        bundle['default_count'] = default_count

    self._save_data()


def get_bundle_details(self, bundle_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a bundle.

    Args:
        bundle_id: Bundle to query

    Returns:
        Dictionary with bundle metadata and statistics

    Raises:
        ValueError: If bundle not found
    """
    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    bundle_data = bundles[bundle_id]

    # Calculate category distribution
    from core.source_system.source_registry import get_source_registry
    registry = get_source_registry()

    categories = {}
    for source_id in bundle_data.get('sources', []):
        config = registry.get_source_config(source_id)
        if config:
            category = getattr(config, 'category', 'other')
            categories[category] = categories.get(category, 0) + 1

    return {
        'bundle_id': bundle_id,
        'description': bundle_data.get('description', ''),
        'sources': bundle_data.get('sources', []),
        'default_count': bundle_data.get('default_count', 20),
        'total_sources': len(bundle_data.get('sources', [])),
        'category_distribution': categories
    }


def list_bundles(self) -> List[Dict[str, Any]]:
    """
    Get list of all bundles with basic info.

    Returns:
        List of bundle dictionaries with id, description, source_count
    """
    bundles_list = []
    for bundle_id, bundle_data in self.data.get('bundles', {}).items():
        bundles_list.append({
            'bundle_id': bundle_id,
            'description': bundle_data.get('description', ''),
            'source_count': len(bundle_data.get('sources', [])),
            'default_count': bundle_data.get('default_count', 20)
        })

    return sorted(bundles_list, key=lambda x: x['bundle_id'])


def copy_bundle(
    self,
    source_bundle_id: str,
    target_bundle_id: str,
    new_description: str = None
) -> None:
    """
    Copy existing bundle to new bundle.

    Args:
        source_bundle_id: Bundle to copy from
        target_bundle_id: New bundle ID
        new_description: Optional new description (else copies original)

    Raises:
        ValueError: If source not found or target exists
    """
    bundles = self.data.get('bundles', {})

    if source_bundle_id not in bundles:
        raise ValueError(f"Source bundle '{source_bundle_id}' not found")

    if target_bundle_id in bundles:
        raise ValueError(f"Target bundle '{target_bundle_id}' already exists")

    source_data = bundles[source_bundle_id]

    bundles[target_bundle_id] = {
        'description': new_description or source_data.get('description', ''),
        'sources': source_data.get('sources', []).copy(),
        'default_count': source_data.get('default_count', 20)
    }

    self._save_data()


def add_sources_to_bundle(
    self,
    bundle_id: str,
    source_ids: List[str]
) -> int:
    """
    Add multiple sources to bundle.

    Args:
        bundle_id: Target bundle
        source_ids: List of source IDs to add

    Returns:
        Number of sources added (excludes duplicates)

    Raises:
        ValueError: If bundle not found
    """
    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    bundle_sources = bundles[bundle_id].get('sources', [])
    added_count = 0

    for source_id in source_ids:
        if source_id not in bundle_sources:
            bundle_sources.append(source_id)
            added_count += 1

    if added_count > 0:
        self._save_data()

    return added_count


def remove_sources_from_bundle(
    self,
    bundle_id: str,
    source_ids: List[str]
) -> int:
    """
    Remove multiple sources from bundle.

    Args:
        bundle_id: Target bundle
        source_ids: List of source IDs to remove

    Returns:
        Number of sources removed

    Raises:
        ValueError: If bundle not found
    """
    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    bundle_sources = bundles[bundle_id].get('sources', [])
    removed_count = 0

    for source_id in source_ids:
        if source_id in bundle_sources:
            bundle_sources.remove(source_id)
            removed_count += 1

    if removed_count > 0:
        self._save_data()

    return removed_count
```

**Testing Requirements:**
- Unit test each method
- Test error cases (not found, duplicates, invalid inputs)
- Test YAML preservation (comments, formatting)
- Test atomic operations (save failures)

**Estimated Time:** 10-12 hours (implementation + tests)

---

### 1.2 Create BundleValidator Class

**File:** `core/source_system/bundle_validator.py` (new file)
**Lines:** ~150 lines

```python
"""
Bundle validation logic.
Validates bundle IDs, descriptions, source IDs, and integrity.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation operation."""
    valid: bool
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class BundleValidator:
    """Validates bundle operations and data."""

    # Bundle ID pattern: lowercase letters, numbers, underscores
    BUNDLE_ID_PATTERN = re.compile(r'^[a-z0-9_]+$')
    BUNDLE_ID_MAX_LENGTH = 30
    DESCRIPTION_MAX_LENGTH = 200
    DEFAULT_COUNT_MIN = 1
    DEFAULT_COUNT_MAX = 100

    def __init__(self, bundle_manager=None, source_registry=None):
        """
        Args:
            bundle_manager: BundleManager instance for existence checks
            source_registry: SourceRegistry instance for source validation
        """
        self._bundle_manager = bundle_manager
        self._source_registry = source_registry

    def validate_bundle_id(self, bundle_id: str) -> ValidationResult:
        """
        Validate bundle ID format.

        Args:
            bundle_id: Bundle identifier to validate

        Returns:
            ValidationResult with errors if invalid
        """
        errors = []

        if not bundle_id:
            errors.append("Bundle ID cannot be empty")
            return ValidationResult(valid=False, errors=errors)

        if len(bundle_id) > self.BUNDLE_ID_MAX_LENGTH:
            errors.append(
                f"Bundle ID too long (max {self.BUNDLE_ID_MAX_LENGTH} chars)"
            )

        if not self.BUNDLE_ID_PATTERN.match(bundle_id):
            errors.append(
                "Bundle ID must contain only lowercase letters, "
                "numbers, and underscores"
            )

        if bundle_id.startswith('_') or bundle_id.endswith('_'):
            errors.append("Bundle ID cannot start or end with underscore")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )

    def validate_bundle_unique(self, bundle_id: str) -> ValidationResult:
        """
        Check if bundle ID is unique.

        Args:
            bundle_id: Bundle identifier to check

        Returns:
            ValidationResult with error if duplicate
        """
        if not self._bundle_manager:
            return ValidationResult(valid=True, errors=[])

        existing_bundles = self._bundle_manager.get_bundle_names()

        if bundle_id in existing_bundles:
            return ValidationResult(
                valid=False,
                errors=[f"Bundle '{bundle_id}' already exists"]
            )

        return ValidationResult(valid=True, errors=[])

    def validate_description(self, description: str) -> ValidationResult:
        """
        Validate bundle description.

        Args:
            description: Description text

        Returns:
            ValidationResult with errors if invalid
        """
        errors = []

        if not description or not description.strip():
            errors.append("Description cannot be empty")
        elif len(description) > self.DESCRIPTION_MAX_LENGTH:
            errors.append(
                f"Description too long (max {self.DESCRIPTION_MAX_LENGTH} chars)"
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )

    def validate_default_count(self, count: int) -> ValidationResult:
        """
        Validate default article count.

        Args:
            count: Article count

        Returns:
            ValidationResult with errors if invalid
        """
        errors = []

        if not isinstance(count, int):
            errors.append("Default count must be an integer")
        elif count < self.DEFAULT_COUNT_MIN or count > self.DEFAULT_COUNT_MAX:
            errors.append(
                f"Default count must be between "
                f"{self.DEFAULT_COUNT_MIN} and {self.DEFAULT_COUNT_MAX}"
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )

    def validate_source_ids(
        self,
        source_ids: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate source IDs against registry.

        Args:
            source_ids: List of source IDs to validate

        Returns:
            Tuple of (valid_ids, invalid_ids)
        """
        if not self._source_registry:
            # Cannot validate without registry, assume all valid
            return source_ids, []

        available_sources = self._source_registry.get_available_sources()

        valid_ids = []
        invalid_ids = []

        for source_id in source_ids:
            if source_id in available_sources:
                valid_ids.append(source_id)
            else:
                invalid_ids.append(source_id)

        return valid_ids, invalid_ids

    def validate_bundle_exists(self, bundle_id: str) -> ValidationResult:
        """
        Check if bundle exists.

        Args:
            bundle_id: Bundle identifier

        Returns:
            ValidationResult with error if not found
        """
        if not self._bundle_manager:
            return ValidationResult(valid=True, errors=[])

        existing_bundles = self._bundle_manager.get_bundle_names()

        if bundle_id not in existing_bundles:
            return ValidationResult(
                valid=False,
                errors=[f"Bundle '{bundle_id}' not found"]
            )

        return ValidationResult(valid=True, errors=[])

    def validate_not_protected(self, bundle_id: str) -> ValidationResult:
        """
        Check if bundle is protected from modification.

        Args:
            bundle_id: Bundle identifier

        Returns:
            ValidationResult with error if protected
        """
        protected_bundles = ['all']  # System bundles

        if bundle_id in protected_bundles:
            return ValidationResult(
                valid=False,
                errors=[f"Cannot modify '{bundle_id}' (system bundle)"]
            )

        return ValidationResult(valid=True, errors=[])
```

**Testing Requirements:**
- Test each validation method
- Test edge cases (empty strings, special chars, boundary values)
- Test with and without dependencies (bundle_manager, registry)

**Estimated Time:** 6-8 hours (implementation + tests)

---

### 1.3 Create Data Models

**File:** `core/source_system/bundle_models.py` (new file)
**Lines:** ~80 lines

```python
"""
Data models for bundle management.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


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
    sources: List[str] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    valid: bool
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


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
    details: Dict[str, any]
    backup_id: Optional[str] = None
```

**Testing Requirements:**
- Test dataclass instantiation
- Test default values
- Test property methods

**Estimated Time:** 2-3 hours (implementation + tests)

---

### 1.4 Unit Tests for Phase 1

**File:** `tests/test_bundle_manager.py`
**Lines:** ~300 lines

**Test Coverage:**
- BundleManager CRUD operations
- BundleValidator all validation methods
- Data models
- Error handling
- YAML preservation

**Test Cases:**
```python
class TestBundleManagerCRUD:
    def test_create_bundle_success()
    def test_create_bundle_duplicate_id()
    def test_create_bundle_invalid_id()
    def test_delete_bundle_success()
    def test_delete_bundle_not_found()
    def test_delete_protected_bundle()
    def test_update_metadata_success()
    def test_update_metadata_not_found()
    def test_get_bundle_details()
    def test_list_bundles()
    def test_copy_bundle()

class TestBundleValidator:
    def test_validate_bundle_id_valid()
    def test_validate_bundle_id_invalid_chars()
    def test_validate_bundle_id_too_long()
    def test_validate_description_valid()
    def test_validate_description_empty()
    def test_validate_default_count_valid()
    def test_validate_default_count_out_of_range()
    def test_validate_source_ids()
```

**Estimated Time:** 4-5 hours

---

## Phase 2: Source Management Operations
**Duration:** 7-9 days (25-30 hours)
**Goal:** Implement source-to-bundle operations

### 2.1 Extend BundleManager with Move Operations

**File:** `core/source_system/bundle_manager.py`
**Lines to Add:** ~100 lines

**New Methods:**

```python
def move_source_between_bundles(
    self,
    source_id: str,
    from_bundle_id: str,
    to_bundle_id: str,
    copy_mode: bool = False
) -> Dict[str, bool]:
    """
    Move or copy source from one bundle to another.

    Args:
        source_id: Source to move/copy
        from_bundle_id: Source bundle
        to_bundle_id: Target bundle
        copy_mode: If True, copy (keep in source). If False, move (remove from source)

    Returns:
        Dictionary with 'added' and 'removed' status

    Raises:
        ValueError: If bundles not found or source not in from_bundle
    """
    bundles = self.data.get('bundles', {})

    if from_bundle_id not in bundles:
        raise ValueError(f"Source bundle '{from_bundle_id}' not found")

    if to_bundle_id not in bundles:
        raise ValueError(f"Target bundle '{to_bundle_id}' not found")

    from_sources = bundles[from_bundle_id].get('sources', [])
    to_sources = bundles[to_bundle_id].get('sources', [])

    if source_id not in from_sources:
        raise ValueError(
            f"Source '{source_id}' not in bundle '{from_bundle_id}'"
        )

    result = {'added': False, 'removed': False}

    # Add to target bundle
    if source_id not in to_sources:
        to_sources.append(source_id)
        result['added'] = True

    # Remove from source bundle (if move mode)
    if not copy_mode:
        from_sources.remove(source_id)
        result['removed'] = True

    self._save_data()
    return result


def get_source_bundle_memberships(
    self,
    source_id: str
) -> List[str]:
    """
    Get list of bundles containing a source.

    Args:
        source_id: Source to query

    Returns:
        List of bundle IDs containing the source
    """
    bundles = self.data.get('bundles', {})
    memberships = []

    for bundle_id, bundle_data in bundles.items():
        if source_id in bundle_data.get('sources', []):
            memberships.append(bundle_id)

    return sorted(memberships)


def bulk_add_by_category(
    self,
    bundle_id: str,
    category: str
) -> int:
    """
    Add all sources from a category to bundle.

    Args:
        bundle_id: Target bundle
        category: Source category (tech, news, etc.)

    Returns:
        Number of sources added

    Raises:
        ValueError: If bundle not found
    """
    from core.source_system.source_registry import get_source_registry

    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    registry = get_source_registry()
    bundle_sources = bundles[bundle_id].get('sources', [])
    added_count = 0

    for source_id in registry.get_available_sources():
        config = registry.get_source_config(source_id)
        if config and getattr(config, 'category', None) == category:
            if source_id not in bundle_sources:
                bundle_sources.append(source_id)
                added_count += 1

    if added_count > 0:
        self._save_data()

    return added_count


def bulk_remove_by_category(
    self,
    bundle_id: str,
    category: str
) -> int:
    """
    Remove all sources from a category from bundle.

    Args:
        bundle_id: Target bundle
        category: Source category (tech, news, etc.)

    Returns:
        Number of sources removed

    Raises:
        ValueError: If bundle not found
    """
    from core.source_system.source_registry import get_source_registry

    bundles = self.data.get('bundles', {})
    if bundle_id not in bundles:
        raise ValueError(f"Bundle '{bundle_id}' not found")

    registry = get_source_registry()
    bundle_sources = bundles[bundle_id].get('sources', [])
    removed_count = 0

    sources_to_remove = []
    for source_id in bundle_sources:
        config = registry.get_source_config(source_id)
        if config and getattr(config, 'category', None) == category:
            sources_to_remove.append(source_id)

    for source_id in sources_to_remove:
        bundle_sources.remove(source_id)
        removed_count += 1

    if removed_count > 0:
        self._save_data()

    return removed_count
```

**Estimated Time:** 6-8 hours (implementation + tests)

---

### 2.2 Integration Tests for Phase 2

**File:** `tests/test_bundle_source_operations.py`
**Lines:** ~200 lines

**Test Cases:**
```python
class TestSourceBundleOperations:
    def test_move_source_move_mode()
    def test_move_source_copy_mode()
    def test_move_source_not_in_bundle()
    def test_get_source_memberships()
    def test_bulk_add_by_category()
    def test_bulk_remove_by_category()
```

**Estimated Time:** 4-5 hours

---

## Phase 3: UI Integration
**Duration:** 6-8 days (20-25 hours)
**Goal:** Create interactive UI and integrate with menu

### 3.1 Create BundleUI Component

**File:** `core/source_system/bundle_ui.py` (new file)
**Lines:** ~400 lines

**Implementation:**

```python
"""
User interface components for bundle management.
Uses questionary for consistent menu design.
"""

import questionary
from typing import List, Dict, Optional
from prompt_toolkit.styles import Style

from core.source_system.bundle_models import BundleData


# Consistent orange theme
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),
    ('question', 'bold'),
    ('selected', 'fg:#d75f00'),
    ('pointer', 'fg:#d75f00 bold'),
    ('answer', 'fg:#d75f00'),
])


class BundleUI:
    """Interactive UI for bundle management."""

    def __init__(self):
        self.style = custom_style

    def show_bundle_menu(self) -> Optional[str]:
        """
        Show main bundle management menu.

        Returns:
            Selected action or None if cancelled
        """
        choices = [
            questionary.Choice("Create New Bundle", "create"),
            questionary.Choice("Edit Bundle Metadata", "edit"),
            questionary.Choice("Delete Bundle", "delete"),
            questionary.Separator(),
            questionary.Choice("Add Sources to Bundle", "add_sources"),
            questionary.Choice("Remove Sources from Bundle", "remove_sources"),
            questionary.Choice("Move Sources Between Bundles", "move_sources"),
            questionary.Separator(),
            questionary.Choice("Copy Bundle", "copy"),
            questionary.Choice("View All Bundles", "list"),
            questionary.Separator("─" * 50),
            questionary.Choice("Back to Source Management", "back"),
        ]

        return questionary.select(
            "  Bundle Management - Select an option:",
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    def prompt_create_bundle(self) -> Optional[BundleData]:
        """
        Prompt user for new bundle information.

        Returns:
            BundleData or None if cancelled
        """
        print("\n--- Create New Bundle ---")

        # Bundle ID
        bundle_id = questionary.text(
            "  Bundle ID (lowercase_with_underscores):",
            style=self.style,
            qmark="",
        ).ask()

        if not bundle_id:
            return None

        # Description
        description = questionary.text(
            "  Description:",
            style=self.style,
            qmark="",
        ).ask()

        if not description:
            return None

        # Default count
        default_count_str = questionary.text(
            "  Default article count (default: 20):",
            default="20",
            style=self.style,
            qmark="",
        ).ask()

        if not default_count_str:
            return None

        try:
            default_count = int(default_count_str)
        except ValueError:
            self.show_error("Invalid number for default count")
            return None

        return BundleData(
            bundle_id=bundle_id,
            description=description,
            default_count=default_count
        )

    def prompt_select_bundle(
        self,
        bundles: List[Dict[str, any]],
        message: str = "  Select a bundle:"
    ) -> Optional[str]:
        """
        Prompt user to select a bundle from list.

        Args:
            bundles: List of bundle dictionaries
            message: Prompt message

        Returns:
            Selected bundle_id or None if cancelled
        """
        choices = []

        for bundle in bundles:
            label = f"  {bundle['bundle_id']:20} ({bundle['source_count']} sources)"
            choices.append(questionary.Choice(label, bundle['bundle_id']))

        choices.append(questionary.Separator())
        choices.append(questionary.Choice("Cancel", "cancel"))

        selected = questionary.select(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
        ).ask()

        return None if selected == "cancel" else selected

    def prompt_select_sources(
        self,
        sources: Dict[str, str],
        current_selections: List[str] = None,
        message: str = "  Select sources:",
        group_by_category: bool = True
    ) -> Optional[List[str]]:
        """
        Prompt user to multi-select sources.

        Args:
            sources: Dict of source_id -> display_name
            current_selections: Pre-selected source IDs
            message: Prompt message
            group_by_category: Whether to group sources by category

        Returns:
            List of selected source IDs or None if cancelled
        """
        from core.source_system.source_registry import get_source_registry

        if current_selections is None:
            current_selections = []

        choices = []

        if group_by_category:
            # Group sources by category
            registry = get_source_registry()
            categories = {}

            for source_id, display_name in sources.items():
                config = registry.get_source_config(source_id)
                category = getattr(config, 'category', 'other') if config else 'other'
                if category not in categories:
                    categories[category] = []
                categories[category].append((source_id, display_name))

            # Build choices with category headers
            for category, category_sources in sorted(categories.items()):
                choices.append(questionary.Separator(f"\n  {category.upper()}"))
                for source_id, display_name in sorted(category_sources):
                    label = f"  {source_id:15} → {display_name}"
                    choices.append(questionary.Choice(
                        label,
                        source_id,
                        checked=source_id in current_selections
                    ))
        else:
            # Simple list
            for source_id, display_name in sorted(sources.items()):
                label = f"  {source_id:15} → {display_name}"
                choices.append(questionary.Choice(
                    label,
                    source_id,
                    checked=source_id in current_selections
                ))

        selected = questionary.checkbox(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use Space to select, Enter to confirm)",
        ).ask()

        return selected if selected is not None else None

    def show_bundle_details(self, bundle_info: Dict[str, any]) -> None:
        """
        Display detailed bundle information.

        Args:
            bundle_info: Bundle information dictionary
        """
        print("\n" + "─" * 70)
        print(f"\033[38;5;202m  Bundle Details\033[0m")
        print("─" * 70)

        print(f"\n  \033[1mID:\033[0m             {bundle_info['bundle_id']}")
        print(f"  \033[1mDescription:\033[0m    {bundle_info['description']}")
        print(f"  \033[1mDefault Count:\033[0m  {bundle_info['default_count']}")
        print(f"  \033[1mTotal Sources:\033[0m  {bundle_info['total_sources']}")

        if bundle_info.get('category_distribution'):
            print(f"\n  \033[1mCategory Distribution:\033[0m")
            for category, count in sorted(bundle_info['category_distribution'].items()):
                print(f"    {category:15} {count} sources")

        if bundle_info.get('sources'):
            print(f"\n  \033[1mSources:\033[0m")
            for source_id in sorted(bundle_info['sources']):
                print(f"    • {source_id}")

        print("\n" + "─" * 70)
        input("\n  Press Enter to continue...")

    def prompt_confirm(
        self,
        message: str,
        details: List[str] = None
    ) -> bool:
        """
        Prompt user for confirmation.

        Args:
            message: Confirmation question
            details: Optional list of detail lines to show

        Returns:
            True if confirmed, False otherwise
        """
        if details:
            print()
            for detail in details:
                print(f"  {detail}")
            print()

        return questionary.confirm(
            f"  {message}",
            default=False,
            style=self.style,
            qmark="",
        ).ask()

    def show_success(self, message: str) -> None:
        """Display success message."""
        print(f"\n  \033[32m✓\033[0m {message}")

    def show_error(self, message: str) -> None:
        """Display error message."""
        print(f"\n  \033[31m✗\033[0m {message}")

    def show_info(self, message: str) -> None:
        """Display informational message."""
        print(f"\n  ℹ {message}")
```

**Estimated Time:** 10-12 hours (implementation + manual testing)

---

### 3.2 Create BundleService Orchestrator

**File:** `core/source_system/bundle_service.py` (new file)
**Lines:** ~300 lines

**Implementation:**

```python
"""
Service layer for bundle management.
Orchestrates BundleManager, BundleValidator, and BundleUI.
"""

from typing import Optional
from pathlib import Path

from core.source_system.bundle_manager import BundleManager
from core.source_system.bundle_validator import BundleValidator
from core.source_system.bundle_ui import BundleUI
from core.source_system.source_registry import get_source_registry
from core.logging_config import get_logger


class BundleService:
    """
    Service for bundle management operations.
    Coordinates validation, UI, and persistence.
    """

    def __init__(
        self,
        bundles_path: Path,
        ui: BundleUI = None,
        logger = None
    ):
        """
        Args:
            bundles_path: Path to bundles.yml
            ui: BundleUI instance (creates if None)
            logger: Logger instance (creates if None)
        """
        self.manager = BundleManager(str(bundles_path))
        self.validator = BundleValidator(
            bundle_manager=self.manager,
            source_registry=get_source_registry()
        )
        self.ui = ui or BundleUI()
        self.logger = logger or get_logger(__name__)

    def execute_create_bundle(self) -> None:
        """Execute bundle creation workflow."""
        self.logger.info("Starting create bundle workflow")

        # Prompt for bundle data
        bundle_data = self.ui.prompt_create_bundle()
        if not bundle_data:
            self.ui.show_info("Bundle creation cancelled")
            return

        # Validate bundle ID
        id_result = self.validator.validate_bundle_id(bundle_data.bundle_id)
        if not id_result.valid:
            for error in id_result.errors:
                self.ui.show_error(error)
            return

        # Check uniqueness
        unique_result = self.validator.validate_bundle_unique(bundle_data.bundle_id)
        if not unique_result.valid:
            for error in unique_result.errors:
                self.ui.show_error(error)
            return

        # Validate description
        desc_result = self.validator.validate_description(bundle_data.description)
        if not desc_result.valid:
            for error in desc_result.errors:
                self.ui.show_error(error)
            return

        # Validate default count
        count_result = self.validator.validate_default_count(bundle_data.default_count)
        if not count_result.valid:
            for error in count_result.errors:
                self.ui.show_error(error)
            return

        # Create bundle
        try:
            self.manager.create_bundle(
                bundle_id=bundle_data.bundle_id,
                description=bundle_data.description,
                default_count=bundle_data.default_count
            )

            self.ui.show_success(
                f"Bundle '{bundle_data.bundle_id}' created successfully"
            )
            self.logger.info(f"Created bundle: {bundle_data.bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to create bundle: {e}")
            self.logger.error(f"Bundle creation failed: {e}")

    def execute_delete_bundle(self) -> None:
        """Execute bundle deletion workflow."""
        self.logger.info("Starting delete bundle workflow")

        # Get bundles list
        bundles = self.manager.list_bundles()
        if not bundles:
            self.ui.show_info("No bundles available to delete")
            return

        # Select bundle
        bundle_id = self.ui.prompt_select_bundle(
            bundles,
            message="  Select bundle to delete:"
        )

        if not bundle_id:
            self.ui.show_info("Bundle deletion cancelled")
            return

        # Check if protected
        protected_result = self.validator.validate_not_protected(bundle_id)
        if not protected_result.valid:
            for error in protected_result.errors:
                self.ui.show_error(error)
            return

        # Get bundle details for confirmation
        bundle_info = self.manager.get_bundle_details(bundle_id)

        # Confirm deletion
        details = [
            f"Bundle: {bundle_id}",
            f"Description: {bundle_info['description']}",
            f"Sources: {bundle_info['total_sources']}"
        ]

        confirmed = self.ui.prompt_confirm(
            f"Delete bundle '{bundle_id}'?",
            details=details
        )

        if not confirmed:
            self.ui.show_info("Bundle deletion cancelled")
            return

        # Delete bundle
        try:
            self.manager.delete_bundle(bundle_id)
            self.ui.show_success(f"Bundle '{bundle_id}' deleted successfully")
            self.logger.info(f"Deleted bundle: {bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to delete bundle: {e}")
            self.logger.error(f"Bundle deletion failed: {e}")

    # Similar methods for:
    # - execute_edit_bundle()
    # - execute_add_sources()
    # - execute_remove_sources()
    # - execute_move_source()
    # - execute_copy_bundle()
    # - execute_list_bundles()
```

**Estimated Time:** 8-10 hours (implementation + integration)

---

### 3.3 Integrate with Interactive Menu

**File:** `core/interactive.py`
**Lines to Add:** ~30 lines

**Changes:**

```python
def _handle_manage_sources_flow():
    """Handles the logic for source management submenu."""
    while True:
        with suppress_logging():
            action = questionary.select(
                "  Source Management - Select an option:",
                choices=[
                    questionary.Choice("Add New Source from RSS Feed", "add_rss"),
                    questionary.Choice("Generate Custom Source Config", "generate_config"),
                    questionary.Choice("Remove Existing Sources", "remove"),
                    questionary.Choice("List All Sources", "list_sources"),
                    questionary.Choice("Test a Source", "test_source"),
                    questionary.Choice("Manage Bundles", "manage_bundles"),  # NEW
                    questionary.Separator(),
                    questionary.Choice("Back to Main Menu", "back"),
                ],
                style=custom_style,
                qmark="",
                pointer="▶",
                instruction="\n   (Use arrow keys to navigate)",
            ).ask()

        if not action or action == 'back':
            return

        if action == 'add_rss':
            _handle_add_source_from_rss()
        elif action == 'generate_config':
            _handle_generate_config()
        elif action == 'remove':
            _handle_remove_source()
        elif action == 'list_sources':
            _handle_list_sources()
        elif action == 'test_source':
            _handle_test_source()
        elif action == 'manage_bundles':  # NEW
            _handle_manage_bundles()


def _handle_manage_bundles():
    """Handle bundle management submenu."""
    from pathlib import Path
    from core.source_system.bundle_service import BundleService

    bundles_path = Path(__file__).parent.parent / "sources" / "active" / "bundles.yml"
    service = BundleService(bundles_path)

    while True:
        action = service.ui.show_bundle_menu()

        if not action or action == 'back':
            return

        if action == 'create':
            service.execute_create_bundle()
        elif action == 'edit':
            service.execute_edit_bundle()
        elif action == 'delete':
            service.execute_delete_bundle()
        elif action == 'add_sources':
            service.execute_add_sources()
        elif action == 'remove_sources':
            service.execute_remove_sources()
        elif action == 'move_sources':
            service.execute_move_source()
        elif action == 'copy':
            service.execute_copy_bundle()
        elif action == 'list':
            service.execute_list_bundles()
```

**Estimated Time:** 2-3 hours (integration + testing)

---

## Phase 4: Safety Features and Polish
**Duration:** 5-7 days (15-20 hours)
**Goal:** Add backup/restore, comprehensive error handling, documentation

### 4.1 Create BundleBackupManager

**File:** `core/source_system/bundle_backup_manager.py` (new file)
**Lines:** ~200 lines

**Implementation:**

```python
"""
Backup and restore system for bundle management.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.source_system.bundle_models import BackupMetadata


class BundleBackupManager:
    """Manages backups of bundles.yml file."""

    def __init__(self, bundles_path: Path, backup_dir: Path = None):
        """
        Args:
            bundles_path: Path to bundles.yml
            backup_dir: Path to backup directory (default: backups/bundles/)
        """
        self.bundles_path = bundles_path

        if backup_dir is None:
            backup_dir = bundles_path.parent.parent.parent / "backups" / "bundles"

        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, operation: str = "manual") -> BackupMetadata:
        """
        Create backup of current bundles.yml.

        Args:
            operation: Description of operation (for backup ID)

        Returns:
            BackupMetadata with backup information
        """
        timestamp = datetime.now()
        backup_id = f"bundle_{operation}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        backup_file = self.backup_dir / f"{backup_id}.yml"

        # Copy file
        shutil.copy2(self.bundles_path, backup_file)

        # Count bundles in backup
        import yaml
        with open(backup_file, 'r') as f:
            data = yaml.safe_load(f)
            bundles = list(data.get('bundles', {}).keys())

        return BackupMetadata(
            backup_id=backup_id,
            timestamp=timestamp,
            file_path=backup_file,
            bundle_count=len(bundles),
            bundles=bundles
        )

    def list_backups(self, limit: int = 10) -> List[BackupMetadata]:
        """
        List available backups.

        Args:
            limit: Maximum number of backups to return

        Returns:
            List of BackupMetadata, sorted by timestamp (newest first)
        """
        backup_files = sorted(
            self.backup_dir.glob("bundle_*.yml"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        backups = []
        for backup_file in backup_files[:limit]:
            # Parse backup metadata
            backup_id = backup_file.stem
            timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime)

            # Count bundles
            import yaml
            try:
                with open(backup_file, 'r') as f:
                    data = yaml.safe_load(f)
                    bundles = list(data.get('bundles', {}).keys())
            except:
                bundles = []

            backups.append(BackupMetadata(
                backup_id=backup_id,
                timestamp=timestamp,
                file_path=backup_file,
                bundle_count=len(bundles),
                bundles=bundles
            ))

        return backups

    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore bundles.yml from backup.

        Args:
            backup_id: Backup identifier

        Returns:
            True if successful, False otherwise
        """
        backup_file = self.backup_dir / f"{backup_id}.yml"

        if not backup_file.exists():
            raise ValueError(f"Backup '{backup_id}' not found")

        # Create safety backup of current state
        self.create_backup(operation="pre_restore")

        # Restore backup
        shutil.copy2(backup_file, self.bundles_path)

        return True

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backups, keeping most recent.

        Args:
            keep_count: Number of backups to keep

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(limit=9999)  # Get all

        if len(backups) <= keep_count:
            return 0

        deleted_count = 0
        for backup in backups[keep_count:]:
            backup.file_path.unlink()
            deleted_count += 1

        return deleted_count
```

**Estimated Time:** 5-6 hours (implementation + tests)

---

### 4.2 Integrate Backup System

Modify BundleService to create automatic backups before destructive operations.

**Estimated Time:** 2-3 hours

---

### 4.3 Documentation

**Files to Create/Update:**
- `docs/bundle-management.md` - User guide
- `docs/api/bundle-management-api.md` - API documentation
- Update `CLAUDE.md` with bundle management commands
- Update `README.md` with bundle management features

**Estimated Time:** 4-5 hours

---

### 4.4 Final Testing and Bug Fixes

**Activities:**
- End-to-end testing of all workflows
- Manual UI testing
- Performance testing
- Edge case testing
- Bug fixes from testing

**Estimated Time:** 4-6 hours

---

## Testing Strategy Summary

### Unit Tests
- **BundleManager:** All CRUD operations (~15 tests)
- **BundleValidator:** All validation methods (~12 tests)
- **BundleBackupManager:** Backup/restore operations (~8 tests)
- **Data Models:** Model instantiation and properties (~5 tests)

**Total Unit Tests:** ~40 tests
**Target Coverage:** > 90%

### Integration Tests
- **Source operations:** Move, copy, bulk operations (~10 tests)
- **End-to-end workflows:** Create → Add sources → Delete (~8 tests)
- **Backup/restore:** Full cycle tests (~5 tests)

**Total Integration Tests:** ~23 tests
**Target Coverage:** > 80%

### Manual Testing
- **UI navigation:** All menu paths reachable
- **Error handling:** Clear error messages
- **Confirmation prompts:** Appear for destructive ops
- **YAML integrity:** Comments and formatting preserved

---

## Deployment Checklist

### Pre-Deployment
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing completed
- [ ] Documentation complete
- [ ] Code review passed
- [ ] Performance benchmarks met

### Deployment
- [ ] Create backup of bundles.yml
- [ ] Deploy code to production
- [ ] Verify interactive menu loads
- [ ] Test create bundle operation
- [ ] Test delete bundle operation
- [ ] Monitor for errors

### Post-Deployment
- [ ] User acceptance testing
- [ ] Monitor error logs
- [ ] Collect user feedback
- [ ] Create post-mortem document

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| YAML corruption | Atomic writes, automatic backups, validation |
| Data loss | Backup before every destructive operation |
| UI bugs | Comprehensive manual testing, staged rollout |
| Performance issues | Optimize file I/O, cache parsed data |
| User confusion | Clear UI labels, confirmation prompts, help text |

---

## Success Metrics

**Quantitative:**
- 100% of bundle operations succeed without errors
- 0 YAML corruption incidents
- < 300ms for all operations
- > 90% unit test coverage
- > 80% integration test coverage

**Qualitative:**
- Users can manage bundles without YAML editing
- Clear error messages guide users
- UI consistent with existing design
- Positive user feedback (> 8/10)

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | Week 1 (20-25h) | Extended BundleManager, BundleValidator, Data models, Unit tests |
| Phase 2 | Week 2 (25-30h) | Source operations, Move/copy, Bulk operations, Integration tests |
| Phase 3 | Week 3 (20-25h) | BundleUI, BundleService, Menu integration, Manual testing |
| Phase 4 | Week 4 (15-20h) | Backup system, Documentation, Final testing, Bug fixes |
| **Total** | **4 weeks (80-100h)** | **Complete bundle management system** |

---

## Next Steps

1. **Review PRD and Implementation Plan** with stakeholders
2. **Get approval** for phase 1 implementation
3. **Set up development branch** for bundle management
4. **Begin Phase 1 implementation** (BundleManager extension)
5. **Regular progress updates** after each phase

---

**Document Status:** READY FOR REVIEW
**Author:** Implementation Team
**Reviewer:** Product Owner, Tech Lead
**Approval Required:** YES
