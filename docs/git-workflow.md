# Git Commit and Push Tutorial

## Prerequisites

- Git installed and configured
- Repository cloned locally
- Changes made to files

## Basic Workflow

### 1. Check Status

See what files have been modified:

```bash
git status
```

Example output:
```
On branch main
Changes not staged for commit:
  modified:   core/article_fetcher.py

Untracked files:
  core/conversion_executor.py
```

### 2. Review Changes

See what changed in a specific file:

```bash
git diff core/article_fetcher.py
```

See all changes:

```bash
git diff
```

### 3. Stage Files

Add specific file:

```bash
git add core/article_fetcher.py
```

Add multiple files:

```bash
git add core/article_fetcher.py core/conversion_executor.py
```

Add all changes:

```bash
git add .
```

Add all files in a directory:

```bash
git add core/
```

### 4. Check Staged Files

```bash
git status
```

Example output:
```
On branch main
Changes to be committed:
  modified:   core/article_fetcher.py
  new file:   core/conversion_executor.py
```

### 5. Commit Changes

Simple commit:

```bash
git commit -m "Fix hanging issue"
```

Multi-line commit (recommended):

```bash
git commit -m "$(cat <<'EOF'
Fix hanging issue caused by nested ThreadPoolExecutor deadlock

Problem:
- Batch processing created nested thread pools
- Caused deadlock when processing multiple articles

Solution:
- Created shared conversion executor
- All conversions use single pool

Impact:
- Batch fetch now completes in 7.5s vs indefinite hang
EOF
)"
```

Alternative multi-line approach:

```bash
git commit -m "Fix hanging issue" -m "Details about the fix" -m "Impact: batch processing now works"
```

### 6. Verify Commit

View last commit:

```bash
git log -1
```

View last 5 commits (one line each):

```bash
git log --oneline -5
```

### 7. Push to Remote

Push to main branch:

```bash
git push
```

Push specific branch:

```bash
git push origin main
```

Force push (use with caution):

```bash
git push --force
```

## Complete Example

```bash
# 1. Check what changed
git status

# 2. Review changes
git diff

# 3. Stage files
git add core/article_fetcher.py core/conversion_executor.py

# 4. Verify staging
git status

# 5. Commit with message
git commit -m "Fix hanging issue caused by nested ThreadPoolExecutor deadlock"

# 6. Verify commit
git log --oneline -1

# 7. Push to remote
git push
```

## Common Scenarios

### Unstage a File

```bash
git reset HEAD core/article_fetcher.py
```

### Unstage All Files

```bash
git reset HEAD
```

### Amend Last Commit

Add forgotten file to last commit:

```bash
git add forgotten_file.py
git commit --amend --no-edit
```

Change last commit message:

```bash
git commit --amend -m "New commit message"
```

### Discard Changes

Discard changes in a file (DANGEROUS):

```bash
git checkout -- core/article_fetcher.py
```

Discard all changes (DANGEROUS):

```bash
git reset --hard HEAD
```

### View Commit History

Detailed history:

```bash
git log
```

One-line history:

```bash
git log --oneline
```

Last N commits:

```bash
git log -5
```

With file changes:

```bash
git log --stat
```

### Check Remote Status

See remote URL:

```bash
git remote -v
```

See if local is ahead/behind remote:

```bash
git status
```

Fetch remote changes without merging:

```bash
git fetch
```

## Best Practices

### Commit Messages

**Good:**
```
Fix hanging issue in batch processing

- Created shared conversion executor
- Prevents nested ThreadPoolExecutor deadlock
- Test: ./capcat fetch hn --count 3 completes in 7.5s
```

**Bad:**
```
fix bug
```

### Commit Frequency

- Commit logical units of work
- One feature/fix per commit
- Commit working code (don't break main branch)

### Before Pushing

1. Review your changes: `git diff`
2. Test your code
3. Check commit message: `git log -1`
4. Verify you're on correct branch: `git branch`

### File Organization

Stage files by category:

```bash
# Core changes
git add core/

# Documentation
git add docs/

# Tests
git add tests/

# Commit each group separately
git commit -m "Update core functionality"
git add docs/
git commit -m "Update documentation"
```

## Troubleshooting

### Merge Conflicts

If push fails due to remote changes:

```bash
# Pull remote changes
git pull

# Resolve conflicts in files
# Edit files to fix conflicts

# Stage resolved files
git add conflicted_file.py

# Complete merge
git commit -m "Merge remote changes"

# Push
git push
```

### Wrong Commit Message

Just committed with wrong message:

```bash
git commit --amend -m "Correct message"
```

Already pushed (use with caution):

```bash
git commit --amend -m "Correct message"
git push --force
```

### Committed to Wrong Branch

Move last commit to new branch:

```bash
# Create new branch with current changes
git branch feature-branch

# Reset current branch to previous commit
git reset --hard HEAD~1

# Switch to new branch
git checkout feature-branch
```

### Undo Last Commit (Keep Changes)

```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)

```bash
git reset --hard HEAD~1
```

## Advanced Tips

### Interactive Staging

Stage parts of files:

```bash
git add -p core/article_fetcher.py
```

### View Specific Commit

```bash
git show d44f50d
```

### Compare Commits

```bash
git diff d44f50d..HEAD
```

### Clean Untracked Files

See what would be removed:

```bash
git clean -n
```

Remove untracked files:

```bash
git clean -f
```

Remove untracked files and directories:

```bash
git clean -fd
```

## Quick Reference

```bash
# Status and info
git status              # Check working directory status
git log --oneline -5    # View recent commits
git diff                # See unstaged changes
git diff --staged       # See staged changes

# Staging
git add file.py         # Stage specific file
git add .               # Stage all changes
git reset HEAD file.py  # Unstage file

# Committing
git commit -m "msg"     # Commit with message
git commit --amend      # Modify last commit

# Pushing
git push                # Push to remote
git push origin main    # Push to specific branch
git pull                # Pull remote changes

# Undo
git reset --soft HEAD~1 # Undo commit, keep changes
git reset --hard HEAD~1 # Undo commit, discard changes
git checkout -- file.py # Discard file changes
```

## Capcat-Specific Workflow

### Standard Fix/Feature

```bash
# 1. Make changes to code
# 2. Test changes
./capcat fetch hn --count 3

# 3. Stage and commit
git add core/
git commit -m "Fix: description of fix"

# 4. Push
git push
```

### Documentation Updates

```bash
git add docs/
git commit -m "Update documentation for new feature"
git push
```

### Multiple Related Changes

```bash
# Make all changes
# Stage and commit in logical groups

git add core/conversion_executor.py
git commit -m "Add shared conversion executor"

git add core/article_fetcher.py
git commit -m "Use shared executor in article fetcher"

git add tests/
git commit -m "Add tests for conversion executor"

git push
```

## Safety Rules

1. **Never force push to main** unless absolutely necessary
2. **Always test before committing** to main branch
3. **Pull before push** to avoid conflicts
4. **Commit working code** - don't break the build
5. **Write clear commit messages** for future reference
6. **Review changes** with `git diff` before committing
7. **One logical change per commit** for easy rollback

## Getting Help

```bash
git help commit
git help push
git help add
```

Or online: https://git-scm.com/docs
