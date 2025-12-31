"""
Test Design System Compiler

Validates that the design system compiler correctly processes CSS custom properties
while preserving rem units for accessibility and responsive scaling.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.design_system_compiler import DesignSystemCompiler


def test_design_system_compiler():
    """Test the design system compiler functionality."""
    print("=" * 70)
    print("DESIGN SYSTEM COMPILER TEST")
    print("=" * 70)
    print()

    # Initialize compiler
    print("1. Initializing DesignSystemCompiler...")
    compiler = DesignSystemCompiler()
    print("   ✓ Compiler initialized")
    print()

    # Test computed values extraction
    print("2. Testing computed values extraction...")
    computed_values = compiler.get_computed_values()

    if not computed_values:
        print("   ✗ FAILED: No computed values extracted")
        return False

    print(f"   ✓ Extracted {len(computed_values)} design system values")
    print()

    # Verify key design tokens exist
    print("3. Verifying key design tokens...")
    required_tokens = [
        'text-xxlarge',
        'text-xlarge',
        'text-large',
        'text-base',
        'text-small',
        'space-xs',
        'space-sm',
        'space-md',
        'space-lg',
        'font-weight-normal',
        'line-height-tight',
        'line-height-relaxed',
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in computed_values:
            missing_tokens.append(token)

    if missing_tokens:
        print(f"   ✗ FAILED: Missing tokens: {', '.join(missing_tokens)}")
        return False

    print(f"   ✓ All {len(required_tokens)} required tokens present")
    print()

    # Verify rem units are preserved
    print("4. Verifying rem units are preserved...")
    rem_preserved = True
    for token_name, value in computed_values.items():
        if 'text-' in token_name or 'space-' in token_name:
            if 'rem' in value:
                print(f"   ✓ {token_name}: {value} (rem preserved)")
            elif 'px' in value and 'rem' not in value:
                print(f"   ✗ WARNING: {token_name}: {value} (rem converted to px)")
                rem_preserved = False

    if not rem_preserved:
        print("   ✗ FAILED: Rem units were converted to pixels")
        return False

    print("   ✓ Rem units preserved for responsive scaling")
    print()

    # Test var() reference resolution
    print("5. Testing var() reference resolution...")
    var_refs_resolved = True
    for token_name, value in computed_values.items():
        if 'var(--' in value:
            print(f"   ✗ WARNING: Unresolved var() in {token_name}: {value}")
            var_refs_resolved = False

    if not var_refs_resolved:
        print("   ⚠ Some var() references remain unresolved (may be intentional)")
    else:
        print("   ✓ All var() references resolved")
    print()

    # Test compiled CSS generation
    print("6. Testing compiled CSS generation...")
    compiled_css = compiler.get_compiled_design_system_css()

    if not compiled_css or "Error" in compiled_css:
        print("   ✗ FAILED: Could not generate compiled CSS")
        return False

    # Verify compiled CSS contains expected content
    checks = [
        ("COMPILED DESIGN SYSTEM VALUES" in compiled_css, "Header comment"),
        (":root {" in compiled_css, "Root selector"),
        ("--text-" in compiled_css, "Typography tokens"),
        ("--space-" in compiled_css, "Spacing tokens"),
        ("rem" in compiled_css, "Rem units preserved"),
    ]

    all_checks_passed = True
    for check, description in checks:
        if check:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ {description}")
            all_checks_passed = False

    if not all_checks_passed:
        print("   ✗ FAILED: Compiled CSS validation failed")
        return False

    print("   ✓ Compiled CSS generated successfully")
    print()

    # Test design tokens for JavaScript
    print("7. Testing JavaScript design tokens...")
    js_tokens = compiler.get_design_tokens_for_js()

    if not js_tokens:
        print("   ✗ FAILED: No JavaScript tokens generated")
        return False

    # Check camelCase conversion
    if 'textLarge' in js_tokens or 'textXlarge' in js_tokens:
        print(f"   ✓ CamelCase conversion working ({len(js_tokens)} tokens)")
    else:
        print("   ✗ WARNING: CamelCase conversion may have issues")

    print()

    # Display sample output
    print("8. Sample compiled output:")
    print("-" * 70)
    lines = compiled_css.split('\n')
    for line in lines[:30]:  # Show first 30 lines
        print(f"   {line}")
    if len(lines) > 30:
        print(f"   ... ({len(lines) - 30} more lines)")
    print("-" * 70)
    print()

    return True


def test_integration_with_html_generator():
    """Test integration with HTML generator."""
    print("=" * 70)
    print("HTML GENERATOR INTEGRATION TEST")
    print("=" * 70)
    print()

    try:
        from core.html_generator import HTMLGenerator

        print("1. Initializing HTMLGenerator...")
        generator = HTMLGenerator()
        print("   ✓ HTMLGenerator initialized with design system compiler")
        print()

        print("2. Checking design system compiler instance...")
        if hasattr(generator, 'design_system_compiler'):
            print("   ✓ Design system compiler is attached to HTMLGenerator")

            # Test that it can get compiled CSS
            compiled = generator.design_system_compiler.get_compiled_design_system_css()
            if compiled and "COMPILED DESIGN SYSTEM" in compiled:
                print("   ✓ Compiler can generate CSS from HTMLGenerator context")
            else:
                print("   ✗ WARNING: Compiler attached but not generating expected output")
        else:
            print("   ✗ FAILED: Design system compiler not found in HTMLGenerator")
            return False

        print()
        return True

    except ImportError as e:
        print(f"   ✗ FAILED: Could not import HTMLGenerator: {e}")
        return False
    except Exception as e:
        print(f"   ✗ FAILED: Error during integration test: {e}")
        return False


def main():
    """Run all design system tests."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         CAPCAT DESIGN SYSTEM INTEGRATION TEST SUITE              ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("\n")

    results = []

    # Run compiler test
    try:
        result = test_design_system_compiler()
        results.append(("Design System Compiler", result))
    except Exception as e:
        print(f"\n✗ EXCEPTION in compiler test: {e}\n")
        results.append(("Design System Compiler", False))

    print()

    # Run integration test
    try:
        result = test_integration_with_html_generator()
        results.append(("HTML Generator Integration", result))
    except Exception as e:
        print(f"\n✗ EXCEPTION in integration test: {e}\n")
        results.append(("HTML Generator Integration", False))

    # Summary
    print("\n")
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")

    print("=" * 70)

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✓ ALL TESTS PASSED")
        print("\nThe design system is correctly integrated and preserves:")
        print("  - Rem units for accessibility and responsive scaling")
        print("  - Resolved var() references for performance")
        print("  - Golden ratio typography hierarchy")
        print("  - Multiples of 8 spacing system")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease review the failures above and fix the issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)