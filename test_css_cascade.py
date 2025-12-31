#!/usr/bin/env python3
"""
Test CSS cascade and variable resolution for .feature-card h3
"""

import re
from pathlib import Path

def parse_css_rules(css_content):
    """Extract CSS rules that affect h3 elements"""
    # Find all rules with font-weight
    rules = []

    # Pattern to match CSS rules
    pattern = r'([^{]+)\s*\{([^}]+)\}'
    matches = re.finditer(pattern, css_content, re.DOTALL)

    for match in matches:
        selector = match.group(1).strip()
        properties = match.group(2).strip()

        # Check if this rule affects h3 or font-weight
        if 'h3' in selector or 'font-weight' in properties:
            rules.append({
                'selector': selector,
                'properties': properties
            })

    return rules

def calculate_specificity(selector):
    """
    Calculate CSS specificity (simplified)
    Returns (inline, id, class/attr, element)
    """
    # Remove pseudo-elements and pseudo-classes for simplicity
    selector = re.sub(r'::[a-z-]+', '', selector)
    selector = re.sub(r':[a-z-]+', '', selector)

    id_count = len(re.findall(r'#', selector))
    class_count = len(re.findall(r'\.', selector))
    element_count = len(re.findall(r'\b(h[1-6]|div|span|p|a|li|ul|section|article|header|footer|main|nav)\b', selector))

    return (0, id_count, class_count, element_count)

def main():
    # Read CSS files
    design_system_path = Path('website/css/design-system.css')
    main_css_path = Path('website/css/main.css')

    print("=" * 60)
    print("CSS CASCADE ANALYSIS FOR .feature-card h3")
    print("=" * 60)

    # Check if files exist
    if not design_system_path.exists():
        print(f"ERROR: {design_system_path} not found")
        return

    if not main_css_path.exists():
        print(f"ERROR: {main_css_path} not found")
        return

    # Read main.css
    with open(main_css_path, 'r') as f:
        main_css = f.read()

    # Find all h3-related rules
    h3_rules = []

    # Pattern to match selectors containing h3
    selector_pattern = r'([^{]+h3[^{]*)\s*\{([^}]+)\}'

    for match in re.finditer(selector_pattern, main_css, re.DOTALL):
        selector = match.group(1).strip()
        properties = match.group(2).strip()

        # Extract font-weight if present
        fw_match = re.search(r'font-weight:\s*([^;]+);?', properties)
        font_weight = fw_match.group(1).strip() if fw_match else None

        if font_weight or '.feature-card' in selector:
            specificity = calculate_specificity(selector)
            h3_rules.append({
                'selector': selector,
                'font_weight': font_weight,
                'specificity': specificity,
                'specificity_score': specificity[0] * 1000 + specificity[1] * 100 + specificity[2] * 10 + specificity[3]
            })

    # Sort by specificity and source order
    h3_rules.sort(key=lambda x: x['specificity_score'])

    print("\n📋 H3 RULES (in cascade order - low to high specificity):")
    print("-" * 60)
    for i, rule in enumerate(h3_rules, 1):
        print(f"\n{i}. Selector: {rule['selector']}")
        print(f"   Font-weight: {rule['font_weight'] or '(not set)'}")
        print(f"   Specificity: {rule['specificity']} (score: {rule['specificity_score']})")

    # Find the specific rule for .feature-card h3
    print("\n" + "=" * 60)
    print("🎯 SPECIFIC RULE: .feature-card h3")
    print("=" * 60)

    feature_card_rule = next((r for r in h3_rules if '.feature-card' in r['selector'] and 'h3' in r['selector']), None)

    if feature_card_rule:
        print(f"\nSelector: {feature_card_rule['selector']}")
        print(f"Font-weight: {feature_card_rule['font_weight']}")
        print(f"Specificity: {feature_card_rule['specificity']}")

        # Check if this is overridden by anything
        overriders = [r for r in h3_rules if r['specificity_score'] > feature_card_rule['specificity_score']]
        if overriders:
            print(f"\n⚠️  WARNING: {len(overriders)} rule(s) with higher specificity:")
            for rule in overriders:
                print(f"   - {rule['selector']}")
    else:
        print("❌ .feature-card h3 rule not found!")

    # Check CSS variables
    print("\n" + "=" * 60)
    print("🔍 CSS VARIABLE RESOLUTION")
    print("=" * 60)

    with open(design_system_path, 'r') as f:
        design_system = f.read()

    # Find variable definitions
    var_pattern = r'--([a-z-]+):\s*([^;]+);'
    variables = {}
    for match in re.finditer(var_pattern, design_system):
        var_name = match.group(1)
        var_value = match.group(2).strip()
        variables[var_name] = var_value

    # Resolve weight-display
    print("\nResolving var(--weight-display):")
    if 'weight-display' in variables:
        weight_display = variables['weight-display']
        print(f"  --weight-display: {weight_display}")

        # Check if it references another variable
        if 'var(' in weight_display:
            ref_var = re.search(r'var\(--([^)]+)\)', weight_display)
            if ref_var:
                ref_name = ref_var.group(1)
                if ref_name in variables:
                    print(f"  --{ref_name}: {variables[ref_name]}")
                    print(f"\n✅ RESOLVED: var(--weight-display) = {variables[ref_name]}")
                else:
                    print(f"\n❌ ERROR: --{ref_name} not defined!")
    else:
        print("❌ ERROR: --weight-display not defined!")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()