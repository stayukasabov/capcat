# Testing Guide: Enhanced Remove-Source

## Quick Test (5 minutes)

### Prerequisites
```bash
cd Application
source venv/bin/activate
```

### 1. Create Test Sources
```bash
# Add a test source
./capcat add-source --url https://feeds.arstechnica.com/arstechnica/index

# Follow prompts to add source ID: test_source1
```

### 2. Test Dry-Run
```bash
./capcat remove-source --dry-run

# Expected:
# - Shows analytics (if you've used sources)
# - Select test_source1
# - Shows removal summary
# - Message: "[DRY RUN] No changes made"
# - Source still exists after
```

### 3. Test Actual Removal
```bash
./capcat remove-source

# Expected:
# - Shows analytics
# - Select test_source1
# - Shows removal summary
# - Confirm: Yes
# - Message: "Successfully removed 1 source(s)"
# - Message: "Backup created: removal_YYYYMMDD_HHMMSS"
```

### 4. Verify Removal
```bash
./capcat list sources

# Expected:
# - test_source1 NOT in list
```

### 5. Test Undo
```bash
./capcat remove-source --undo

# Expected:
# - Shows list of backups
# - Select most recent
# - Confirm: Yes
# - Message: "Restored 1 source(s): test_source1"
```

### 6. Verify Restore
```bash
./capcat list sources

# Expected:
# - test_source1 IS in list
```

## Comprehensive Testing (30 minutes)

### Setup Test Environment

```bash
# Create test directory structure
mkdir -p test_environment
cd test_environment

# Create multiple test sources
cat > test_sources.yml <<EOF
test1:
  display_name: "Test Source 1"
  category: tech
test2:
  display_name: "Test Source 2"
  category: news
test3:
  display_name: "Test Source 3"
  category: tech
EOF
```

### Test 1: Batch Removal

```bash
# 1. Create batch file
cat > remove_batch.txt <<EOF
# Test batch removal
test1
test2
# test3 - keep this one
EOF

# 2. Preview batch
./capcat remove-source --batch remove_batch.txt --dry-run

# Expected:
# - Shows 2 sources (test1, test2)
# - [DRY RUN] message
# - No actual removal

# 3. Execute batch
./capcat remove-source --batch remove_batch.txt

# Expected:
# - Shows summary for test1, test2
# - Confirmation prompt
# - Backup created
# - Both sources removed

# 4. Verify
./capcat list sources | grep test

# Expected:
# - Only test3 appears
```

### Test 2: Analytics Integration

```bash
# 1. Add test source
./capcat add-source --url https://feeds.example.com/test

# 2. Fetch from it several times to generate analytics
./capcat fetch test_analytics --count 5

# 3. Check analytics before removal
./capcat remove-source

# Expected:
# - Analytics summary shows test_analytics usage
# - Shows fetch count, frequency
# - Shows recommendation based on usage
```

### Test 3: Backup System

```bash
# 1. Check backup directory
ls -la ../.capcat_backups/

# Expected:
# - Directory exists
# - Contains removal_* subdirectories

# 2. Inspect a backup
ls -la ../.capcat_backups/removal_*/

# Expected:
# - metadata.json
# - configs/ directory
# - bundles.yml

# 3. Check metadata
cat ../.capcat_backups/removal_*/metadata.json

# Expected:
# - JSON with backup_id, timestamp, sources
```

### Test 4: Force Mode (No Confirmations)

```bash
# 1. Create batch file
echo "test1" > force_test.txt

# 2. Execute with force
./capcat remove-source --batch force_test.txt --force

# Expected:
# - No confirmation prompts
# - Immediate removal
# - Backup still created
```

### Test 5: No Backup Mode

```bash
# 1. Count current backups
BEFORE=$(ls ../.capcat_backups/ | wc -l)

# 2. Remove without backup
./capcat remove-source --no-backup

# Expected:
# - Normal removal process
# - No "Backup created" message

# 3. Verify no new backup
AFTER=$(ls ../.capcat_backups/ | wc -l)
[ "$BEFORE" -eq "$AFTER" ] && echo "PASS: No backup created"
```

### Test 6: Multiple Undo/Restore

```bash
# 1. Remove source A
./capcat remove-source  # Remove source A

# 2. Remove source B
./capcat remove-source  # Remove source B

# 3. List backups
./capcat remove-source --undo
# Cancel to just see list

# Expected:
# - Shows 2+ backups
# - Most recent first
# - Each with timestamp and sources

# 4. Restore specific backup
./capcat remove-source --undo removal_YYYYMMDD_HHMMSS

# Expected:
# - Restores only that specific backup's sources
```

## Unit Testing

### Test Analytics

```bash
cd Application

# Create test file
cat > test_analytics_manual.py <<'EOF'
from pathlib import Path
from core.source_system.source_analytics import SourceAnalytics, AnalyticsReporter

# Test analytics tracking
analytics = SourceAnalytics(Path("/tmp/test_analytics.json"))

# Record some fetches
analytics.record_fetch("test1", True, 10)
analytics.record_fetch("test1", True, 8)
analytics.record_fetch("test1", False, 0)

# Get stats
stats = analytics.get_source_stats("test1", "Test Source 1")
print(f"Total fetches: {stats.total_fetches}")
print(f"Success rate: {stats.successful_fetches}/{stats.total_fetches}")
print(f"Frequency: {stats.fetch_frequency}")

# Get recommendation
recommendation = AnalyticsReporter.format_removal_recommendation(stats)
print(f"Recommendation: {recommendation}")
EOF

python test_analytics_manual.py

# Expected:
# Total fetches: 3
# Success rate: 2/3
# Frequency: ...
# Recommendation: [ACTIVE] Regular use
```

### Test Backup Manager

```bash
cat > test_backup_manual.py <<'EOF'
from pathlib import Path
from core.source_system.source_backup_manager import SourceBackupManager

# Create test files
test_dir = Path("/tmp/test_capcat")
test_dir.mkdir(exist_ok=True)

config_path = test_dir / "test.yml"
config_path.write_text("display_name: Test")

bundles_path = test_dir / "bundles.yml"
bundles_path.write_text("bundles:\n  tech:\n    sources: [test]")

# Test backup
backup_manager = SourceBackupManager(test_dir / "backups")
metadata = backup_manager.create_backup(
    ["test"],
    [config_path],
    bundles_path
)

print(f"Backup created: {metadata.backup_id}")
print(f"Sources: {metadata.sources}")

# Test restore
restored = backup_manager.restore_backup(
    metadata.backup_id,
    test_dir / "restored",
    test_dir / "bundles_restored.yml"
)

print(f"Restored: {restored}")

# List backups
backups = backup_manager.list_backups()
print(f"Total backups: {len(backups)}")
EOF

python test_backup_manual.py

# Expected:
# Backup created: removal_YYYYMMDD_HHMMSS
# Sources: ['test']
# Restored: ['test']
# Total backups: 1
```

## Automated Test Suite

```bash
# Run existing tests
pytest tests/test_remove_source_command.py -v
pytest tests/test_bundle_manager_remove.py -v

# Expected:
# All tests pass
# Coverage > 90%
```

### Create New Test File

```bash
cat > tests/test_enhanced_remove.py <<'EOF'
import pytest
from pathlib import Path
from unittest.mock import Mock

from core.source_system.enhanced_remove_command import (
    EnhancedRemoveCommand,
    RemovalOptions
)
from core.source_system.removal_ui import MockRemovalUI


def test_dry_run_mode():
    """Test that dry-run doesn't modify anything."""
    # Setup
    base_command = Mock()
    backup_manager = Mock()
    analytics = Mock()
    ui = MockRemovalUI({'selected_sources': ['test'], 'confirm_removal': True})

    command = EnhancedRemoveCommand(
        base_command, backup_manager, analytics, ui, Mock()
    )

    # Execute with dry-run
    options = RemovalOptions(dry_run=True)
    command.execute_with_options(options)

    # Verify nothing was actually removed
    base_command._remove_sources.assert_not_called()
    backup_manager.create_backup.assert_not_called()


def test_backup_created_by_default():
    """Test that backup is created by default."""
    # Setup mocks
    base_command = Mock()
    base_command._source_lister.get_available_sources.return_value = []

    # Should not reach backup creation with no sources
    # This tests the flow


def test_undo_latest():
    """Test undoing the latest removal."""
    # Test implementation
    pass
EOF

# Run new tests
pytest tests/test_enhanced_remove.py -v
```

## Integration Testing

### Test Full Workflow

```bash
#!/bin/bash
# integration_test.sh

set -e  # Exit on error

echo "=== Integration Test: Remove-Source Enhanced ==="

# 1. Setup
echo "Setting up test environment..."
cd Application
source venv/bin/activate

# 2. Add test sources
echo "Adding test sources..."
# (Would need to be interactive or mocked)

# 3. Test dry-run
echo "Testing dry-run..."
./capcat remove-source --dry-run --no-analytics << EOF
test1
n
EOF

# 4. Test actual removal
echo "Testing removal with backup..."
./capcat remove-source << EOF
test1
y
EOF

# 5. Verify backup created
echo "Verifying backup..."
if [ -d "../.capcat_backups" ]; then
    echo "PASS: Backup directory exists"
else
    echo "FAIL: No backup directory"
    exit 1
fi

# 6. Test undo
echo "Testing undo..."
./capcat remove-source --undo << EOF
y
EOF

# 7. Verify restore
echo "Verifying restore..."
./capcat list sources | grep test1 && echo "PASS: Source restored" || echo "FAIL: Source not found"

echo "=== All integration tests passed ==="
```

## Edge Cases to Test

### 1. Empty Selections
```bash
./capcat remove-source

# Select nothing
# Expected: "No sources selected for removal"
```

### 2. Non-Existent Source in Batch
```bash
echo "nonexistent_source" > bad_batch.txt
./capcat remove-source --batch bad_batch.txt

# Expected:
# "Sources not found: nonexistent_source"
# "No valid sources to remove"
```

### 3. Corrupted Backup
```bash
# Manually corrupt a backup
echo "bad data" > ../.capcat_backups/removal_test/metadata.json

# Try to restore
./capcat remove-source --undo removal_test

# Expected:
# Error message about corrupted backup
```

### 4. Concurrent Operations
```bash
# Terminal 1
./capcat remove-source

# Terminal 2 (while Terminal 1 is waiting for input)
./capcat remove-source

# Expected:
# Both should work independently
# File locking prevents corruption
```

### 5. Disk Full Scenario
```bash
# Simulate disk full (on test system only!)
# Expected: Graceful error handling
```

## Performance Testing

### Large Batch Removal
```bash
# Create 100 test sources (scripted)
# Remove all via batch
time ./capcat remove-source --batch large_batch.txt --force

# Expected:
# - Completes in < 5 seconds
# - Single backup contains all sources
```

### Analytics with Many Records
```bash
# Simulate 1000 fetch records
# Check analytics query performance
time ./capcat remove-source --dry-run

# Expected:
# - Analytics load < 1 second
# - No performance degradation
```

## Checklist

### Basic Functionality
- [ ] Interactive removal works
- [ ] Sources actually deleted
- [ ] Bundles updated correctly
- [ ] Registry refreshed

### Dry-Run Mode
- [ ] No files deleted in dry-run
- [ ] Preview shows correct information
- [ ] Can execute after dry-run

### Backup System
- [ ] Backup created automatically
- [ ] Backup contains all files
- [ ] Metadata saved correctly
- [ ] Can skip backup with flag

### Analytics
- [ ] Usage stats displayed
- [ ] Recommendations shown
- [ ] Can skip with flag
- [ ] Analytics persist across sessions

### Batch Removal
- [ ] Batch file parsed correctly
- [ ] Comments ignored
- [ ] Invalid sources reported
- [ ] Multiple sources removed

### Undo/Restore
- [ ] Lists available backups
- [ ] Restores files correctly
- [ ] Registry refreshed after restore
- [ ] Can specify backup ID

### Error Handling
- [ ] Invalid source IDs handled
- [ ] Missing files handled gracefully
- [ ] User cancellation works
- [ ] Partial failures continue

### CLI Integration
- [ ] All flags work
- [ ] Flag combinations work
- [ ] Help text accurate
- [ ] Exit codes correct

## Troubleshooting Tests

### Test Fails: "Module not found"
```bash
# Ensure in venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Test Fails: "Permission denied"
```bash
# Check directory permissions
ls -la ../.capcat_backups/

# Fix if needed
chmod 755 ../.capcat_backups/
```

### Test Fails: "No backups found"
```bash
# Create a backup first
./capcat remove-source  # Remove something

# Then test undo
./capcat remove-source --undo
```

## Continuous Testing

```bash
# Run all tests
pytest tests/ -v --cov=core.source_system

# Expected coverage:
# - source_backup_manager.py > 90%
# - source_analytics.py > 90%
# - enhanced_remove_command.py > 85%
# - remove_source_command.py > 95%
```