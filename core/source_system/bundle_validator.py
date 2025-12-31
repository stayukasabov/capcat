"""
Bundle validation logic.
Validates bundle IDs, descriptions, source IDs, and integrity.
"""

import re
from typing import List, Tuple
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
