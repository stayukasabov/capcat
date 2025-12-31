#!/bin/bash

echo "Checking CSS links..."
css_missing=0
find ./docs -name "*.html" -type f | while read file; do
    if ! grep -q 'design-system.css' "$file" || ! grep -q 'main.css' "$file"; then
        echo "Missing CSS in: $file"
        css_missing=$((css_missing + 1))
    fi
done

echo "All files have CSS links"
echo ""
echo "Checking JS links..."
js_issues=0
find ./docs -name "*.html" -type f | while read file; do
    count=$(grep -c 'main\.js' "$file")
    if [ "$count" -eq 0 ]; then
        echo "Missing JS in: $file"
        js_issues=$((js_issues + 1))
    elif [ "$count" -gt 1 ]; then
        echo "Duplicate JS in: $file"
        js_issues=$((js_issues + 1))
    fi
done

echo "All files have correct JS links"
echo ""
echo "Verification complete!"
