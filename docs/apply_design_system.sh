#!/bin/bash

# Apply design system CSS and JS to all HTML files in the docs folder
# Removes inline <style> tags and adds links to design-system.css, main.css, and main.js

WEBSITE_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$WEBSITE_ROOT/docs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter
TOTAL_FILES=0
SUCCESS_COUNT=0

# Function to calculate relative path
calculate_relative_path() {
    local html_file="$1"
    local html_dir="$(dirname "$html_file")"
    local rel_path=$(python3 -c "import os.path; print(os.path.relpath('$WEBSITE_ROOT', '$html_dir'))")
    echo "$rel_path"
}

# Function to process a single HTML file
process_html_file() {
    local file="$1"
    echo "Processing: $file"

    # Calculate relative path
    local rel_path=$(calculate_relative_path "$file")

    # Create a temporary file
    local temp_file="${file}.tmp"

    # Read the file and process it
    local in_head=0
    local in_style=0
    local has_design_system=0
    local has_main_css=0
    local has_main_js=0
    local head_closed=0
    local body_end_found=0

    # First pass: check what already exists
    while IFS= read -r line; do
        if [[ "$line" =~ design-system\.css ]]; then
            has_design_system=1
        fi
        if [[ "$line" =~ \"main\.css\" ]] || [[ "$line" =~ \'main\.css\' ]]; then
            has_main_css=1
        fi
        if [[ "$line" =~ \"main\.js\" ]] || [[ "$line" =~ \'main\.js\' ]]; then
            has_main_js=1
        fi
    done < "$file"

    # Second pass: modify the file
    local added_css=0
    local added_js=0

    while IFS= read -r line; do
        # Check if we're in the <head> section
        if [[ "$line" =~ \<head ]]; then
            in_head=1
            echo "$line" >> "$temp_file"
            continue
        fi

        # Check if we're entering a <style> tag
        if [[ "$line" =~ \<style ]]; then
            in_style=1
            echo "  - Removing <style> tag"
            continue
        fi

        # Check if we're exiting a <style> tag
        if [[ "$line" =~ \</style\> ]]; then
            in_style=0
            continue
        fi

        # Skip lines inside <style> tags
        if [ $in_style -eq 1 ]; then
            continue
        fi

        # Add CSS links before </head>
        if [[ "$line" =~ \</head\> ]] && [ $in_head -eq 1 ]; then
            if [ $has_design_system -eq 0 ] && [ $added_css -eq 0 ]; then
                echo "    <link rel=\"stylesheet\" href=\"${rel_path}/css/design-system.css\">" >> "$temp_file"
                echo "    <link rel=\"stylesheet\" href=\"${rel_path}/css/main.css\">" >> "$temp_file"
                echo "  ${GREEN}+ Added design-system.css and main.css${NC}"
                added_css=1
            fi
            in_head=0
            head_closed=1
        fi

        # Add JS before </body>
        if [[ "$line" =~ \</body\> ]]; then
            if [ $has_main_js -eq 0 ] && [ $added_js -eq 0 ]; then
                echo "    <script src=\"${rel_path}/js/main.js\"></script>" >> "$temp_file"
                echo "  ${GREEN}+ Added main.js${NC}"
                added_js=1
            fi
        fi

        # Write the line to temp file
        echo "$line" >> "$temp_file"

    done < "$file"

    # Replace original file with temp file
    mv "$temp_file" "$file"

    echo -e "  ${GREEN}✓ Successfully updated${NC}"
    echo ""

    return 0
}

# Main execution
echo "======================================"
echo "Applying Design System to Docs"
echo "======================================"
echo ""

if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}Error: docs directory not found at $DOCS_DIR${NC}"
    exit 1
fi

# Find all HTML files
while IFS= read -r -d '' file; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    if process_html_file "$file"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
done < <(find "$DOCS_DIR" -name "*.html" -type f -print0)

echo "======================================"
echo "Processed $SUCCESS_COUNT/$TOTAL_FILES files successfully"
echo "======================================"
