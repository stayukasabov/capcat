#!/bin/bash
cd website
find . -name "*.html" -type f | while read file; do
  link=$(grep -o 'href="[^"]*ethical-scraping\.html"' "$file" 2>/dev/null | head -1 | sed 's/href="//;s/"//')
  if [ -n "$link" ]; then
    depth=$(echo "$file" | tr -cd '/' | wc -c)
    echo "$file -> $link (depth: $depth)"
  fi
done | sort
