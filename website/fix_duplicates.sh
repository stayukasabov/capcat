#!/bin/bash

# Remove duplicate main.js script tags

find ./docs -name "*.html" -type f | while read file; do
    count=$(grep -c 'main\.js' "$file")
    if [ "$count" -gt 1 ]; then
        echo "Fixing: $file"
        awk '/<script src=".*main\.js"><\/script>/ {if (!found) {print; found=1} next} 1' "$file" > "${file}.tmp"
        mv "${file}.tmp" "$file"
    fi
done

echo "Done removing duplicates"
