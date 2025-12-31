#!/bin/bash
# Comprehensive fix for all Claude Code command compatibility issues

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Claude Code Commands - Comprehensive Compatibility Fix       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Backup directory
BACKUP_DIR=~/.claude/commands-backup-$(date +%Y%m%d-%H%M%S)
echo "1. Creating backup..."
cp -r ~/.claude/commands "$BACKUP_DIR"
echo "   ✓ Backup saved to: $BACKUP_DIR"
echo ""

# Fix 1: Remove model declarations
echo "2. Removing API-specific model declarations..."
FIXED_COUNT=0
for file in ~/.claude/commands/tools/*.md ~/.claude/commands/workflows/*.md; do
    if grep -q "^model: claude-opus-4-1" "$file" 2>/dev/null; then
        sed -i '' '/^model: claude-opus-4-1$/d' "$file"
        echo "   ✓ Fixed: $(basename $file)"
        ((FIXED_COUNT++))
    fi
done
echo "   Total files fixed: $FIXED_COUNT"
echo ""

# Fix 2: Fix agent name typo
echo "3. Fixing agent name typos..."
FILES_TO_FIX=(
    ~/.claude/commands/tools/multi-agent-review.md
    ~/.claude/commands/workflows/full-review.md
)
for file in "${FILES_TO_FIX[@]}"; do
    if [ -f "$file" ]; then
        sed -i '' 's/architect-reviewer/architect-review/g' "$file"
        echo "   ✓ Fixed: $(basename $file)"
    fi
done
echo ""

# Verification
echo "4. Verification..."
MODEL_COUNT=$(grep -r "^model: claude-opus" ~/.claude/commands/ 2>/dev/null | wc -l | tr -d ' ')
MISSING_AGENTS=$(grep -ro 'subagent_type="[^"]*"' ~/.claude/commands/ 2>/dev/null | \
    cut -d'"' -f2 | sort -u | while read agent; do
        [ ! -f ~/.claude/agents/${agent}.md ] && echo "$agent"
    done)

if [ "$MODEL_COUNT" -eq 0 ]; then
    echo "   ✓ All model declarations removed"
else
    echo "   ⚠️  Warning: $MODEL_COUNT model declarations remain"
fi

if [ -z "$MISSING_AGENTS" ]; then
    echo "   ✓ All referenced agents exist"
else
    echo "   ⚠️  Missing agents:"
    echo "$MISSING_AGENTS" | sed 's/^/      /'
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Fix Complete!                                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Commands are now compatible with Claude Code."
echo ""
echo "Test with:"
echo "  /tools:tdd-refactor look at templates, css and html generator"
echo "  /workflows:tdd-cycle implement new feature"
echo "  /tools:security-scan scan codebase for vulnerabilities"
echo ""
echo "Backup location: $BACKUP_DIR"
