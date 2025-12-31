#!/usr/bin/env python3
"""
Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat.

This script creates production-ready configs with all necessary fields
including discovery methods, selectors, image processing, and templates.
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional


def prompt_text(question: str, default: Optional[str] = None) -> str:
    """
    Prompt user for text input with optional default value.

    Args:
        question: Question to ask the user
        default: Optional default value

    Returns:
        User input or default value
    """
    if default:
        response = input(f"{question} [{default}]: ").strip()
        return response if response else default
    else:
        while True:
            response = input(f"{question}: ").strip()
            if response:
                return response
            print("This field is required.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no question.

    Args:
        question: Question to ask
        default: Default value if user just presses enter

    Returns:
        True for yes, False for no
    """
    default_text = "Y/n" if default else "y/N"
    while True:
        response = input(f"{question} [{default_text}]: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")


def prompt_list(question: str, examples: List[str]) -> List[str]:
    """
    Prompt user for a list of items.

    Args:
        question: Question to ask
        examples: Example values to show

    Returns:
        List of user-provided items
    """
    print(f"\n{question}")
    print(f"Examples: {', '.join(examples)}")
    print("Enter items one per line. Press Enter on empty line to finish.")

    items = []
    while True:
        item = input("  > ").strip()
        if not item:
            break
        items.append(item)

    return items if items else examples


def prompt_choice(question: str, choices: List[str], default: str) -> str:
    """
    Prompt user to choose from a list of options.

    Args:
        question: Question to ask
        choices: List of valid choices
        default: Default choice

    Returns:
        Selected choice
    """
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        response = input(f"Choice [1-{len(choices)}] or Enter for default: ").strip()
        if not response:
            return default
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {len(choices)}")


def generate_config() -> Dict:
    """
    Interactively gather configuration data from user.

    Returns:
        Dictionary containing the complete configuration
    """
    print("=" * 70)
    print("Capcat Source Configuration Generator")
    print("=" * 70)
    print("\nThis script will guide you through creating a comprehensive")
    print("YAML configuration for a new config-driven source.\n")

    config = {}

    # Basic information
    print("\n--- BASIC INFORMATION ---")
    config['source_id'] = prompt_text(
        "Source ID (short lowercase identifier, e.g., 'bbc', 'iq')"
    )
    config['name'] = prompt_text(
        "Internal name",
        default=config['source_id'].upper()
    )
    config['display_name'] = prompt_text(
        "Display name (user-facing)",
        default=config['name']
    )

    # Category
    categories = ['tech', 'techpro', 'news', 'science', 'ai', 'sports']
    config['category'] = prompt_choice(
        "Category",
        categories,
        'tech'
    )

    # URL configuration
    print("\n--- URL CONFIGURATION ---")
    config['base_url'] = prompt_text("Base URL (e.g., https://example.com/news)")

    # Discovery method
    print("\n--- DISCOVERY METHOD ---")
    discovery_method = prompt_choice(
        "How should articles be discovered?",
        ['rss', 'html'],
        'rss'
    )

    config['discovery'] = {
        'method': discovery_method,
        'max_articles': int(prompt_text("Maximum articles to fetch", default="30"))
    }

    if discovery_method == 'rss':
        rss_url = prompt_text("RSS feed URL")
        config['discovery']['rss_url'] = rss_url
        config['rss_url'] = rss_url  # Top-level for backwards compatibility

    # Article selectors (for discovery)
    print("\n--- ARTICLE SELECTORS ---")
    print("CSS selectors to find article links on the main page")
    if discovery_method == 'html':
        article_selectors = prompt_list(
            "Enter article link selectors:",
            ['h2 a[href*="/news/"]', 'h3 a', '.article-link']
        )
    else:
        print("(RSS discovery typically doesn't need custom selectors)")
        if prompt_yes_no("Add custom article selectors anyway?", False):
            article_selectors = prompt_list(
                "Enter article link selectors:",
                ['h2 a', '.headline a']
            )
        else:
            article_selectors = []

    if article_selectors:
        config['article_selectors'] = article_selectors

    # Content selectors
    print("\n--- CONTENT SELECTORS ---")
    print("CSS selectors to extract article content from individual pages")
    content_selectors = prompt_list(
        "Enter content extraction selectors:",
        ['article', '.article-content', '.post-body', 'main']
    )
    config['content_selectors'] = content_selectors

    # Image processing
    print("\n--- IMAGE PROCESSING ---")
    if prompt_yes_no("Configure custom image processing?", True):
        image_selectors = prompt_list(
            "Enter image selectors:",
            ['article img', 'figure img', 'picture img', '.article-body img']
        )
        skip_selectors = prompt_list(
            "Enter selectors for images to skip (nav, ads, etc.):",
            ['nav img', 'header img', 'footer img', '.sidebar img']
        )
        config['image_processing'] = {
            'selectors': image_selectors,
            'skip_selectors': skip_selectors
        }

    # Template configuration
    print("\n--- TEMPLATE CONFIGURATION ---")
    config['supports_comments'] = prompt_yes_no(
        "Does this source support comments?",
        False
    )

    template_variant = 'article-with-comments' if config['supports_comments'] else 'article-no-comments'
    config['template'] = {
        'variant': template_variant,
        'navigation': {
            'show_breadcrumb': True,
            'show_source_link': True
        }
    }

    # Request configuration
    print("\n--- REQUEST CONFIGURATION ---")
    config['timeout'] = int(prompt_text("Request timeout (seconds)", default="15"))
    config['rate_limit'] = float(prompt_text("Rate limit (seconds between requests)", default="1.0"))

    # Skip patterns
    print("\n--- SKIP PATTERNS ---")
    if prompt_yes_no("Add URL patterns to skip (e.g., /about, /contact)?", True):
        skip_patterns = prompt_list(
            "Enter URL patterns to avoid:",
            ['/about', '/contact', '/privacy', '/terms', '/profile']
        )
        config['skip_patterns'] = skip_patterns

    return config


def save_config(config: Dict, output_path: Optional[Path] = None) -> Path:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        output_path: Optional custom output path

    Returns:
        Path to saved file
    """
    if output_path is None:
        # Default location
        script_dir = Path(__file__).parent
        config_dir = script_dir.parent / "sources" / "active" / "config_driven" / "configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        output_path = config_dir / f"{config['source_id']}.yaml"

    # Generate YAML with nice formatting
    yaml_content = f"# {config['display_name']} Configuration\n"

    with open(output_path, 'w') as f:
        f.write(yaml_content)
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)

    return output_path


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive YAML configuration for Capcat sources"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Custom output file path (default: sources/active/config_driven/configs/)'
    )
    return parser.parse_args()


def main():
    """Main entry point for the config generator."""
    try:
        # Parse arguments
        args = parse_args()

        # Generate configuration
        config = generate_config()

        # Show preview
        print("\n" + "=" * 70)
        print("CONFIGURATION PREVIEW")
        print("=" * 70)
        print(yaml.dump(config, sort_keys=False, default_flow_style=False))

        # Confirm save
        if not prompt_yes_no("\nSave this configuration?", True):
            print("Configuration not saved.")
            sys.exit(0)

        # Save with custom output path if provided
        output_path = save_config(config, args.output)
        print(f"\nConfiguration saved to: {output_path}")

        # Next steps
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print(f"1. Review the config: cat {output_path}")
        print(f"2. Test the source: ./capcat fetch {config['source_id']} --count 5")
        print(f"3. Add to bundles if needed: edit sources/active/bundles.yml")
        print()

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
