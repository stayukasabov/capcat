# Scripts Package

## Overview

This package contains the following modules:

- [`scripts.setup_dependencies`](./setup_dependencies.md) - Automated Dependency Setup and Repair Script for Capcat

This script provides robust virtual environment management with:
- Intelligent venv validation and repair
- Dependency verification and installation
- Path corruption detection and fixing
- Fallback mechanisms for common issues
- Comprehensive logging and diagnostics

Usage:
    python3 scripts/setup_dependencies
- [`scripts.update_svg_color`](./update_svg_color.md) - Update SVG fill color in all documentation HTML files
- [`scripts.generate_source_config`](./generate_source_config.md) - Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat
- [`scripts.rename_ink_to_imprint`](./rename_ink_to_imprint.md) - Rename all instances of --cream to --paper in website/css/ files
- [`scripts.run_docs`](./run_docs.md) - Documentation Generation Runner

Convenient script to generate all documentation types
- [`scripts.add_doc_navigation`](./add_doc_navigation.md) - Add chapter navigation links to documentation HTML files
- [`scripts.apply_mermaid_design_system`](./apply_mermaid_design_system.md) - Apply design system CSS variables to Mermaid diagram styling in diagrams/*
- [`scripts.convert_md_tables_to_html`](./convert_md_tables_to_html.md) - Convert Markdown Tables to Centered HTML Tables

Scans all markdown files in website/docs/ directory and converts
markdown tables to centered HTML tables with proper styling
- [`scripts.doc_generator`](./doc_generator.md) - Documentation Generator for Capcat

Automatically extracts and generates comprehensive documentation from the codebase
- [`scripts.replace_menus_with_menu`](./replace_menus_with_menu.md) - Replace 'menus' with 'menu' in text under Mermaid diagrams in diagrams/*
- [`scripts.update_footer_text`](./update_footer_text.md) - Update footer text in website HTML files
- [`scripts.final_extractor`](./final_extractor.md) - This script intelligently extracts meaningful text content from HTML files, 
chunks it, and creates markdown files with placeholders for summaries
- [`scripts.generate_diagrams`](./generate_diagrams.md) - Generate Architecture Diagrams for Capcat

Creates Mermaid diagrams for system architecture, data flow, and component relationships
- [`scripts.replace_exhaustive`](./replace_exhaustive.md) - Replace "Exhaustive" with "Comprehensive" in all website files
- [`scripts.intelligent_html_extractor`](./intelligent_html_extractor.md) - This script intelligently extracts text content from HTML files, 
chunks it, and creates markdown files with placeholders for summaries
- [`scripts.extract_and_summarize`](./extract_and_summarize.md) - This script extracts text from HTML files in the AgentBrew folder, 
chunks it, and creates markdown files with placeholders for summaries
