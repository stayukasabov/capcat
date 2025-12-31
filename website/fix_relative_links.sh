#!/bin/bash

# Fix relative links across all HTML files in the website

WEBSITE_ROOT="/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/website"

cd "$WEBSITE_ROOT" || exit 1

echo "Fixing relative links in all HTML files..."

# Function to calculate relative path
calculate_relative_path() {
    local html_file="$1"
    local html_dir="$(dirname "$html_file")"
    local rel_path=$(python3 -c "import os.path; print(os.path.relpath('$WEBSITE_ROOT', '$html_dir'))")
    echo "$rel_path"
}

# Process all HTML files
find docs -name "*.html" -type f | while read -r html_file; do
    echo "Processing: $html_file"

    # Calculate relative path to website root
    rel_path=$(calculate_relative_path "$html_file")

    # Create temp file
    temp_file="${html_file}.tmp"

    # Replace absolute paths with relative paths
    # Fix file:// URLs - remove them completely and use relative paths
    sed -E "s|file:///Volumes/DRIVE%20B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat%20copy/Application/website/||g" "$html_file" > "$temp_file"

    # Move temp file back
    mv "$temp_file" "$html_file"

    echo "Fixed: $html_file"
done

echo "All files processed!"
