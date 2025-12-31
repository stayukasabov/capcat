#!/bin/bash

# Remove duplicate main.js script tags

WEBSITE_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$WEBSITE_ROOT/docs"

echo "Removing duplicate main.js script tags..."

find "$DOCS_DIR" -name "*.html" -type f | while read file; do
    # Check if file has duplicate script tags
    duplicate_count=$(grep -c '<script src=".*main.js"></script>' "$file")

    if [ "$duplicate_count" -gt 1 ]; then
        echo "Fixing: $file (found $duplicate_count instances)"

        # Use sed to remove duplicates - keep only the last occurrence
        # First, temporarily mark the last occurrence
        sed -i '' '/<script src=".*main\.js"><\/script>/{
            x
            /main/{
                d
            }
            x
            s/.*/main/
            x
        }' "$file"
    fi
done

echo "Done!"
