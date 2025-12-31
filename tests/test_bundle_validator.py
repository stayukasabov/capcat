#!/usr/bin/env python3
"""
Comprehensive test suite for BundleValidator.

Tests all validation rules with parameterized tests for thorough coverage.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.source_system.bundle_validator import BundleValidator, ValidationResult


class TestBundleIdValidation:
    """Test bundle ID validation rules."""

    @pytest.mark.parametrize("bundle_id,expected_valid", [
        # Valid IDs
        ("tech", True),
        ("tech_news", True),
        ("ai2025", True),
        ("my_bundle_123", True),
        ("a", True),  # Single character
        ("a" * 30, True),  # Max length

        # Invalid IDs
        ("", False),  # Empty
        ("Tech", False),  # Uppercase
        ("tech news", False),  # Space
        ("tech-news", False),  # Hyphen
        ("tech.news", False),  # Period
        ("tech/news", False),  # Slash
        ("tech@news", False),  # Special char
        ("_tech", False),  # Starts with underscore
        ("tech_", False),  # Ends with underscore
        ("a" * 31, False),  # Too long
    ])
    def test_validate_bundle_id_format(self, bundle_id, expected_valid):
        """Test bundle ID format validation with various inputs."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_bundle_id(bundle_id)

        # Assert
        assert result.valid == expected_valid
        if not expected_valid:
            assert len(result.errors) > 0
        else:
            assert len(result.errors) == 0

    def test_validate_bundle_id_empty_specific_error(self):
        """Test that empty bundle ID has specific error message."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_bundle_id("")

        # Assert
        assert not result.valid
        assert "Bundle ID cannot be empty" in result.errors[0]

    def test_validate_bundle_id_too_long_specific_error(self):
        """Test that too-long bundle ID has specific error message."""
        # Arrange
        validator = BundleValidator()
        long_id = "a" * 31

        # Act
        result = validator.validate_bundle_id(long_id)

        # Assert
        assert not result.valid
        assert "too long" in result.errors[0]
        assert "30 chars" in result.errors[0]

    def test_validate_bundle_id_invalid_chars_specific_error(self):
        """Test that invalid characters have specific error message."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_bundle_id("Tech-News")

        # Assert
        assert not result.valid
        assert "lowercase letters, numbers, and underscores" in result.errors[0]

    def test_validate_bundle_id_underscore_position_error(self):
        """Test that leading/trailing underscores have specific error."""
        # Arrange
        validator = BundleValidator()

        # Act
        result_leading = validator.validate_bundle_id("_tech")
        result_trailing = validator.validate_bundle_id("tech_")

        # Assert
        assert not result_leading.valid
        assert "cannot start or end with underscore" in result_leading.errors[0]
        assert not result_trailing.valid
        assert "cannot start or end with underscore" in result_trailing.errors[0]


class TestBundleUniquenessValidation:
    """Test bundle uniqueness validation."""

    def test_validate_bundle_unique_no_manager(self):
        """Test validation without bundle manager."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_bundle_unique("new_bundle")

        # Assert - Should pass without manager
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_bundle_unique_new_bundle(self):
        """Test that new bundle ID is valid."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news', 'science']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act
        result = validator.validate_bundle_unique("new_bundle")

        # Assert
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_bundle_unique_duplicate_bundle(self):
        """Test that duplicate bundle ID is rejected."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news', 'science']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act
        result = validator.validate_bundle_unique("tech")

        # Assert
        assert not result.valid
        assert len(result.errors) == 1
        assert "already exists" in result.errors[0]
        assert "tech" in result.errors[0]


class TestDescriptionValidation:
    """Test bundle description validation."""

    @pytest.mark.parametrize("description,expected_valid", [
        # Valid descriptions
        ("Tech news and articles", True),
        ("A", True),  # Single character
        ("a" * 200, True),  # Max length
        ("Valid description with special chars: @#$%", True),
        ("Valid with numbers 123", True),

        # Invalid descriptions
        ("", False),  # Empty
        ("   ", False),  # Only whitespace
        ("\t\n", False),  # Only whitespace chars
        ("a" * 201, False),  # Too long
    ])
    def test_validate_description_format(self, description, expected_valid):
        """Test description validation with various inputs."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_description(description)

        # Assert
        assert result.valid == expected_valid
        if not expected_valid:
            assert len(result.errors) > 0
        else:
            assert len(result.errors) == 0

    def test_validate_description_empty_specific_error(self):
        """Test that empty description has specific error message."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_description("")

        # Assert
        assert not result.valid
        assert "Description cannot be empty" in result.errors[0]

    def test_validate_description_too_long_specific_error(self):
        """Test that too-long description has specific error message."""
        # Arrange
        validator = BundleValidator()
        long_desc = "a" * 201

        # Act
        result = validator.validate_description(long_desc)

        # Assert
        assert not result.valid
        assert "too long" in result.errors[0]
        assert "200 chars" in result.errors[0]

    def test_validate_description_whitespace_only(self):
        """Test that whitespace-only description is rejected."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_description("   \t\n   ")

        # Assert
        assert not result.valid
        assert "cannot be empty" in result.errors[0]


class TestDefaultCountValidation:
    """Test default article count validation."""

    @pytest.mark.parametrize("count,expected_valid", [
        # Valid counts
        (1, True),    # Minimum
        (20, True),   # Typical
        (50, True),   # Mid-range
        (100, True),  # Maximum

        # Invalid counts
        (0, False),    # Too low
        (-1, False),   # Negative
        (101, False),  # Too high
        (1000, False), # Way too high
    ])
    def test_validate_default_count_range(self, count, expected_valid):
        """Test default count validation with various values."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_default_count(count)

        # Assert
        assert result.valid == expected_valid
        if not expected_valid:
            assert len(result.errors) > 0
        else:
            assert len(result.errors) == 0

    def test_validate_default_count_type_error(self):
        """Test that non-integer count is rejected."""
        # Arrange
        validator = BundleValidator()

        # Act
        result_str = validator.validate_default_count("20")
        result_float = validator.validate_default_count(20.5)
        result_none = validator.validate_default_count(None)

        # Assert
        assert not result_str.valid
        assert "must be an integer" in result_str.errors[0]
        assert not result_float.valid
        assert not result_none.valid

    def test_validate_default_count_range_error_message(self):
        """Test that out-of-range count has specific error message."""
        # Arrange
        validator = BundleValidator()

        # Act
        result_low = validator.validate_default_count(0)
        result_high = validator.validate_default_count(101)

        # Assert
        assert not result_low.valid
        assert "between 1 and 100" in result_low.errors[0]
        assert not result_high.valid
        assert "between 1 and 100" in result_high.errors[0]


class TestSourceIdValidation:
    """Test source ID validation."""

    def test_validate_source_ids_no_registry(self):
        """Test validation without source registry."""
        # Arrange
        validator = BundleValidator()
        source_ids = ['hn', 'bbc', 'invalid']

        # Act
        valid_ids, invalid_ids = validator.validate_source_ids(source_ids)

        # Assert - Without registry, assume all valid
        assert valid_ids == source_ids
        assert invalid_ids == []

    def test_validate_source_ids_all_valid(self):
        """Test validation with all valid source IDs."""
        # Arrange
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['hn', 'bbc', 'guardian']
        validator = BundleValidator(source_registry=mock_registry)

        # Act
        valid_ids, invalid_ids = validator.validate_source_ids(['hn', 'bbc'])

        # Assert
        assert valid_ids == ['hn', 'bbc']
        assert invalid_ids == []

    def test_validate_source_ids_some_invalid(self):
        """Test validation with mix of valid and invalid IDs."""
        # Arrange
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['hn', 'bbc']
        validator = BundleValidator(source_registry=mock_registry)

        # Act
        valid_ids, invalid_ids = validator.validate_source_ids(
            ['hn', 'invalid1', 'bbc', 'invalid2']
        )

        # Assert
        assert valid_ids == ['hn', 'bbc']
        assert invalid_ids == ['invalid1', 'invalid2']

    def test_validate_source_ids_all_invalid(self):
        """Test validation with all invalid source IDs."""
        # Arrange
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['hn', 'bbc']
        validator = BundleValidator(source_registry=mock_registry)

        # Act
        valid_ids, invalid_ids = validator.validate_source_ids(
            ['invalid1', 'invalid2']
        )

        # Assert
        assert valid_ids == []
        assert invalid_ids == ['invalid1', 'invalid2']

    def test_validate_source_ids_empty_list(self):
        """Test validation with empty source list."""
        # Arrange
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['hn', 'bbc']
        validator = BundleValidator(source_registry=mock_registry)

        # Act
        valid_ids, invalid_ids = validator.validate_source_ids([])

        # Assert
        assert valid_ids == []
        assert invalid_ids == []


class TestBundleExistenceValidation:
    """Test bundle existence validation."""

    def test_validate_bundle_exists_no_manager(self):
        """Test validation without bundle manager."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_bundle_exists("tech")

        # Assert - Should pass without manager
        assert result.valid

    def test_validate_bundle_exists_found(self):
        """Test validation for existing bundle."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news', 'science']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act
        result = validator.validate_bundle_exists("tech")

        # Assert
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_bundle_exists_not_found(self):
        """Test validation for non-existent bundle."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act
        result = validator.validate_bundle_exists("nonexistent")

        # Assert
        assert not result.valid
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]
        assert "nonexistent" in result.errors[0]


class TestProtectedBundleValidation:
    """Test protected bundle validation."""

    @pytest.mark.parametrize("bundle_id,expected_valid", [
        ("tech", True),
        ("news", True),
        ("my_bundle", True),
        ("all", False),  # System bundle
    ])
    def test_validate_not_protected(self, bundle_id, expected_valid):
        """Test protected bundle validation."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_not_protected(bundle_id)

        # Assert
        assert result.valid == expected_valid
        if not expected_valid:
            assert len(result.errors) > 0
            assert "system bundle" in result.errors[0]

    def test_validate_not_protected_all_bundle(self):
        """Test that 'all' bundle is protected."""
        # Arrange
        validator = BundleValidator()

        # Act
        result = validator.validate_not_protected("all")

        # Assert
        assert not result.valid
        assert "Cannot modify 'all'" in result.errors[0]


class TestValidationResultDataclass:
    """Test ValidationResult dataclass functionality."""

    def test_validation_result_basic_creation(self):
        """Test creating ValidationResult with basic parameters."""
        # Arrange & Act
        result = ValidationResult(valid=True, errors=[])

        # Assert
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        # Arrange & Act
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(valid=False, errors=errors)

        # Assert
        assert result.valid is False
        assert result.errors == errors
        assert result.warnings == []

    def test_validation_result_with_warnings(self):
        """Test ValidationResult with warnings."""
        # Arrange & Act
        warnings = ["Warning 1", "Warning 2"]
        result = ValidationResult(valid=True, errors=[], warnings=warnings)

        # Assert
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == warnings

    def test_validation_result_warnings_default(self):
        """Test that warnings default to empty list."""
        # Arrange & Act
        result = ValidationResult(valid=True, errors=[])

        # Assert
        assert isinstance(result.warnings, list)
        assert len(result.warnings) == 0


class TestIntegratedValidation:
    """Test integrated validation scenarios."""

    def test_full_bundle_creation_validation_success(self):
        """Test complete bundle creation validation flow."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act - Validate all aspects of a new bundle
        id_result = validator.validate_bundle_id("ai_research")
        unique_result = validator.validate_bundle_unique("ai_research")
        desc_result = validator.validate_description("AI and research articles")
        count_result = validator.validate_default_count(25)

        # Assert
        assert id_result.valid
        assert unique_result.valid
        assert desc_result.valid
        assert count_result.valid

    def test_full_bundle_creation_validation_failures(self):
        """Test bundle creation validation with multiple failures."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act - Try to create invalid bundle
        id_result = validator.validate_bundle_id("Tech News")  # Invalid: space, caps
        unique_result = validator.validate_bundle_unique("tech")  # Invalid: exists
        desc_result = validator.validate_description("")  # Invalid: empty
        count_result = validator.validate_default_count(0)  # Invalid: too low

        # Assert
        assert not id_result.valid
        assert not unique_result.valid
        assert not desc_result.valid
        assert not count_result.valid

    def test_bundle_edit_validation(self):
        """Test bundle editing validation flow."""
        # Arrange
        mock_manager = Mock()
        mock_manager.get_bundle_names.return_value = ['tech', 'news']
        validator = BundleValidator(bundle_manager=mock_manager)

        # Act - Validate editing existing bundle
        exists_result = validator.validate_bundle_exists("tech")
        not_protected_result = validator.validate_not_protected("tech")
        desc_result = validator.validate_description("Updated tech description")

        # Assert
        assert exists_result.valid
        assert not_protected_result.valid
        assert desc_result.valid

    def test_bundle_delete_validation_protected(self):
        """Test deletion validation for protected bundle."""
        # Arrange
        validator = BundleValidator()

        # Act
        not_protected_result = validator.validate_not_protected("all")

        # Assert
        assert not not_protected_result.valid
        assert "system bundle" in not_protected_result.errors[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.bundle_validator'])
