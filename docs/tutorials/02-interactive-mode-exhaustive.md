# Interactive Mode Exhaustive Reference

Complete documentation of EVERY function, menu, option, and workflow in Capcat's interactive mode.

Source: Application/core/interactive.py

## System Architecture

### Technology Stack

**UI Framework:**
- questionary (prompt_toolkit based)
- ANSI escape codes for terminal control
- Context managers for logging suppression

**Styling:**
```python
# Custom orange theme (Application/core/interactive.py:10-17)
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer (▶)
    ('answer', 'fg:#d75f00'),            # Orange answer
    ('instruction', ''),                  # Instruction text
])
```

**Color Code:** `#d75f00` - Orange (RGB: 215, 95, 0)

### Screen Management

#### position_menu_at_bottom(menu_lines=10)
Location: Application/core/interactive.py:39

**Purpose:** Position cursor for bottom-aligned menu display with ASCII logo at top.

**Parameters:**
- `menu_lines` (int) - Number of lines menu will occupy (default: 10)

**Behavior:**
1. Get terminal size using `shutil.get_terminal_size()`
2. Clear screen with ANSI code `\033[2J`
3. Print ASCII logo (8 lines)
4. Calculate padding: `max(0, terminal_height - menu_lines - logo_lines - 1)`
5. Print newlines for padding
6. Menu appears at bottom

**ASCII Logo:**
```
       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \ / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \_____\__,_|  __/ \___\__,_|\__|
                | |
                |_|
```
Source location: Application/core/interactive.py:54-64

**Terminal Control Codes:**
- `\033[2J` - Clear entire screen
- `\033[H` - Move cursor to home (0,0)
- `\033[38;5;202m` - Orange foreground color
- `\033[0m` - Reset formatting
- `\033[F` - Move cursor up one line
- `\033[K` - Clear line from cursor to end

**Fallback:** If terminal size detection fails, uses standard clear: `print('\033[2J\033[H', end='')`

#### suppress_logging()
Location: Application/core/interactive.py:28

**Purpose:** Context manager to temporarily suppress logging during menu display.

**Implementation:**
```python
@contextlib.contextmanager
def suppress_logging():
    logger = logging.getLogger()
    original_level = logger.level
    logger.setLevel(logging.CRITICAL)  # Suppress everything below CRITICAL
    try:
        yield
    finally:
        logger.setLevel(original_level)  # Restore original level
```

**Usage:**
```python
with suppress_logging():
    response = questionary.select(...).ask()
```

**Purpose:** Prevents log messages from interfering with clean menu display.

## Main Entry Point

### start_interactive_mode()
Location: Application/core/interactive.py:78

**Purpose:** Main interactive loop for Capcat UI.

**Execution Flow:**
1. Initialize `first_run = True` flag
2. Enter infinite while loop
3. Position menu at bottom (10 lines)
4. Suppress logging
5. Show main menu with questionary
6. Process user selection
7. Call handler function
8. Return to step 2

**Main Menu Options:**

```
| Display Text                              | Action Value     | Handler Function                   |
|-------------------------------------------|------------------|------------------------------------|
| Catch articles from a bundle of sources  | bundle           | _handle_bundle_flow()              |
| Catch articles from a list of sources    | fetch            | _handle_fetch_flow()               |
| Catch from a single source               | single_source    | _handle_single_source_flow()       |
| Catch a single article by URL            | single_url       | _handle_single_url_flow()          |
| Manage Sources (add/remove/configure)    | manage_sources   | _handle_manage_sources_flow()      |
| Exit                                      | exit             | Return (exits function)            |
```

**Prompt Text:**
- First run: "  What would you like me to do?"
- Subsequent: "  Select an option:"

**Navigation:**
- Arrow keys: Move selection
- Enter: Confirm selection
- Ctrl+C: Exit (returns `None` from `.ask()`)

**Terminal Output:**
```
       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \ / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \_____\__,_|  __/ \___\__,_|\__|
                | |
                |_|

  What would you like me to do?

  > Catch articles from a bundle of sources
    Catch articles from a list of sources
    Catch from a single source
    Catch a single article by URL
    Manage Sources (add/remove/configure)
    Exit

   (Use arrow keys to navigate)
```

**Selection Echo Handling:**
```python
# Clear questionary's selection echo and show custom message
print('\033[F\033[K', end='')  # Move up, clear line
print(f"  Selected option: {action_names.get(action, action)}")
```

**Exit Conditions:**
- User selects "Exit"
- User presses Ctrl+C
- `action` is `None`
- `action == 'exit'`

Result: Prints "Exiting interactive mode." and returns to shell.

## Source Management Submenu

### _handle_manage_sources_flow()
Location: Application/core/interactive.py:132

**Purpose:** Display and handle source management submenu operations.

**Menu Options:**

```
| Display Text                     | Action Value      | Handler Function                   |
|----------------------------------|-------------------|------------------------------------|
| Add New Source from RSS Feed     | add_rss           | _handle_add_source_from_rss()      |
| Generate Custom Source Config    | generate_config   | _handle_generate_config()          |
| Remove Existing Sources          | remove            | _handle_remove_source()            |
| List All Sources                 | list_sources      | _handle_list_sources()             |
| Test a Source                    | test_source       | _handle_test_source()              |
| Manage Bundles                   | manage_bundles    | _handle_manage_bundles()           |
| (separator line)                 | N/A               | questionary.Separator()            |
| Back to Main Menu               | back              | Return to main menu                |
```

**Loop Structure:**
```python
while True:
    # Show menu with suppress_logging()
    action = questionary.select(...).ask()

    if not action or action == 'back':
        return  # Exit to main menu

    # Call handler based on action
    if action == 'add_rss':
        _handle_add_source_from_rss()
    # ... etc
```

**Navigation:** Same as main menu (arrow keys, Enter, Ctrl+C)

### _handle_add_source_from_rss()
Location: Application/core/interactive.py:171

**Purpose:** Interactively add new RSS-based source.

**Workflow:**

**Step 1: URL Input**
```python
print("  (Use Ctrl+C to go back)")
url = questionary.text(
    "  Enter the RSS feed URL:",
    style=custom_style,
    qmark="",
).ask()
```

**Validation:**
- If `url is None` or empty: Print "No URL provided. Returning to menu." and return
- Otherwise: Proceed to step 2

**Step 2: RSS Introspection**
```python
from cli import add_source, get_available_sources
add_source(url)  # Calls Application/cli.py:200
```

**add_source() performs:**
1. RSS feed inspection with `RssFeedIntrospector(url)`
2. Source ID suggestion from feed title
3. Category selection
4. Config generation
5. Optional bundle assignment
6. Optional test fetch

**Step 3: Confirmation**
```python
sources = get_available_sources()
print(f"\n[OK] Active sources: {len(sources)}")
input("\nPress Enter to continue...")
```

**Error Handling:**
```python
except Exception as e:
    print(f"Error adding source: {e}")
input("\nPress Enter to continue...")
```

**Complete Terminal Flow:**
```
  (Use Ctrl+C to go back)
  Enter the RSS feed URL: https://techcrunch.com/feed/

Attempting to add new source from: https://techcrunch.com/feed/
Inspecting RSS feed...
[OK] Feed 'TechCrunch' found.

--- Configure New Source ---
  Source ID (alphanumeric): techcrunch
  Select category: tech
  Add to bundle? Yes
  Select bundle: tech
[OK] Added 'techcrunch' to bundle 'tech'.

--- Running Test Fetch ---
  Test fetch? (recommended) Yes
[OK] Source added and verified successfully!

[OK] Active sources: 16

Press Enter to continue...
```

### _handle_generate_config()
Location: Application/core/interactive.py:200

**Purpose:** Launch interactive config generator script.

**Workflow:**

**Step 1: Confirmation**
```python
print("\n--- Generate Custom Source Configuration ---")
print("This will launch the interactive config generator.\n")

confirm = questionary.confirm(
    "  Continue?",
    default=True,
    style=custom_style,
    qmark="",
).ask()
```

**Step 2: Script Launch**
```python
import subprocess
script_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "scripts",
    "generate_source_config.py"
)

result = subprocess.run([sys.executable, script_path], check=False)
```

**Script Path:** Application/scripts/generate_source_config.py

**Step 3: Result Handling**
```python
if result.returncode != 0:
    print(f"\nConfig generation exited with code: {result.returncode}")

input("\nPress Enter to continue...")
```

**Error Handling:**
```python
except Exception as e:
    print(f"Error launching config generator: {e}")
    input("\nPress Enter to continue...")
```

**Terminal Output:**
```
--- Generate Custom Source Configuration ---
This will launch the interactive config generator.

  Continue? Yes

[Interactive config generator launches]
[User goes through wizard...]
[Config saved to sources/active/config_driven/configs/newsource.yaml]

Press Enter to continue...
```

### _handle_remove_source()
Location: Application/core/interactive.py:237

**Purpose:** Launch interactive source removal tool with enhanced features.

**Workflow:**

**Step 1: Service Initialization**
```python
from core.source_system.remove_source_service import create_remove_source_service
from core.source_system.enhanced_remove_command import RemovalOptions

service = create_remove_source_service()
command = service._create_remove_source_command()
```

**Step 2: Options Configuration**
```python
options = RemovalOptions(
    dry_run=False,           # No preview mode in interactive
    create_backup=True,      # Always create backup
    show_analytics=True,     # Show usage statistics
    batch_file=None,         # No batch file in interactive
    force=False              # Always confirm
)
```

**Step 3: Enhanced Command Execution**
```python
from core.source_system.removal_ui import QuestionaryRemovalUI
from core.source_system.enhanced_remove_command import EnhancedRemoveCommand
from core.source_system.source_backup_manager import SourceBackupManager
from core.source_system.source_analytics import SourceAnalytics

enhanced_command = EnhancedRemoveCommand(
    base_command=command,
    backup_manager=SourceBackupManager(),
    analytics=SourceAnalytics(),
    ui=QuestionaryRemovalUI(),
    logger=get_logger(__name__)
)

enhanced_command.execute_with_options(options)
```

**Step 4: Confirmation**
```python
from cli import get_available_sources
sources = get_available_sources()
print(f"\n[OK] Active sources: {len(sources)}")
input("\nPress Enter to continue...")
```

**Interactive Removal Flow:**
1. Display all sources with checkbox selection
2. Show usage analytics for each source
3. User selects sources with spacebar
4. Confirm removal
5. Create automatic backup
6. Remove sources
7. Display results

**Terminal Output:**
```
--- Remove Sources ---
This will launch the interactive source removal tool.

Select sources to remove (Space to select, Enter to confirm):
  [ ] hn              Hacker News
  [x] oldsite         Old Site
  [x] discontinued    Discontinued Source
  [ ] bbc             BBC News

Usage Analytics:
  oldsite: Last used 90 days ago, 5 articles
  discontinued: Last used 180 days ago, 0 articles

Confirm removal? Yes

[OK] Backup created: .capcat-backups/backup_20251125_143022/
[OK] Removed 2 sources successfully

[OK] Active sources: 14

Press Enter to continue...
```

### _handle_list_sources()
Location: Application/core/interactive.py:287

**Purpose:** Display all sources grouped by category with interactive details view.

**Workflow:**

**Step 1: Source Collection**
```python
from cli import get_available_sources
from core.source_system.source_registry import get_source_registry

sources = get_available_sources()  # Dict[source_id, display_name]
registry = get_source_registry()
```

**Step 2: Category Grouping**
```python
categories = {}  # Dict[category, List[Tuple[source_id, display_name]]]

for source_id, display_name in sorted(sources.items()):
    try:
        config = registry.get_source_config(source_id)
        category = config.category if config and hasattr(config, 'category') else 'other'
    except:
        category = 'other'

    if category not in categories:
        categories[category] = []

    categories[category].append((source_id, display_name))
```

**Step 3: Menu Construction**
```python
choices = []

# Header
choices.append(questionary.Separator(f"\n  Available Sources ({len(sources)} total)"))
choices.append(questionary.Separator())

# Grouped sources
for category, source_list in sorted(categories.items()):
    # Category header
    choices.append(questionary.Separator(f"  {category.upper()}"))

    # Sources in category
    for source_id, display_name in source_list:
        formatted_name = f"  {source_id:15} → {display_name}"
        choices.append(questionary.Choice(formatted_name, source_id))

    # Blank line
    choices.append(questionary.Separator())

# Footer
choices.append(questionary.Separator("─" * 50))
choices.append(questionary.Choice("Back to Source Management", "back"))
```

**Step 4: Interactive Selection**
```python
selected = questionary.select(
    "  Browse sources (select to view details):",
    choices=choices,
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use arrow keys, Enter to view details)",
).ask()
```

**Step 5: Detail View (if source selected)**
```python
if selected and selected != 'back':
    _show_source_details(selected, registry)
    _handle_list_sources()  # Recursive call to return to listing
```

**Terminal Output:**
```
  Available Sources (15 total)

  TECH
    hn              → Hacker News
    lb              → Lobsters
    iq              → InfoQ

  NEWS
    bbc             → BBC News
    guardian        → The Guardian

  SCIENCE
    nature          → Nature News

─────────────────────────────────────────────────
  Back to Source Management

  Browse sources (select to view details):

   (Use arrow keys, Enter to view details)
```

### _show_source_details(source_id, registry)
Location: Application/core/interactive.py:351

**Purpose:** Display detailed information about a selected source.

**Parameters:**
- `source_id` (str) - Source identifier
- `registry` (SourceRegistry) - Registry instance

**Display Format:**
```python
print("\n" + "─" * 70)
print(f"\033[38;5;202m  Source Details\033[0m")  # Orange heading
print("─" * 70)
```

**Information Displayed:**

1. **Core Information:**
   - ID
   - Name (display_name)
   - Category

2. **Base URL:**
   ```python
   if hasattr(config, 'base_url'):
       print(f"  \033[1mBase URL:\033[0m     {config.base_url}")
   ```

3. **Discovery Method:**
   ```python
   if hasattr(config, 'discovery') and hasattr(config.discovery, 'method'):
       print(f"  \033[1mDiscovery:\033[0m    {config.discovery.method}")

       # RSS URLs if available
       if config.discovery.method == 'rss' and hasattr(config.discovery, 'rss_urls'):
           if hasattr(rss_urls, 'primary'):
               print(f"  \033[1mRSS Feed:\033[0m     {rss_urls.primary}")
   ```

4. **Source Type:**
   ```python
   source_type = "Config-driven (YAML)" if hasattr(config, 'article_selectors') else "Custom (Python)"
   print(f"  \033[1mType:\033[0m         {source_type}")
   ```

**Terminal Output:**
```
──────────────────────────────────────────────────────────────────────
  Source Details
──────────────────────────────────────────────────────────────────────

  ID:           hn
  Name:         Hacker News
  Category:     tech
  Base URL:     https://news.ycombinator.com/
  Discovery:    api
  Type:         Custom (Python)

──────────────────────────────────────────────────────────────────────

  Press Enter to continue...
```

**Error Handling:**
```python
except Exception as e:
    print(f"\n  Error loading source details: {e}")
input("\n  Press Enter to continue...")
```

### _handle_test_source()
Location: Application/core/interactive.py:396

**Purpose:** Test a source by fetching 3 sample articles.

**Workflow:**

**Step 1: Source Selection**
```python
from cli import get_available_sources

sources = get_available_sources()
source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
source_choices.append(questionary.Separator())
source_choices.append(questionary.Choice("Back", "back"))

source_id = questionary.select(
    "  Select source to test:",
    choices=source_choices,
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use arrow keys to navigate)",
).ask()
```

**Step 2: Test Execution**
```python
print(f"\n--- Testing Source: {source_id} ---")
print("Fetching 3 articles...\n")

from capcat import run_app
args = ['fetch', source_id, '--count', '3']
run_app(args)
```

**Step 3: Result Display**
```python
print(f"\n[OK] Source '{source_id}' test completed")
```

**Error Handling:**
```python
except SystemExit as e:
    if e.code != 0:
        print(f"\n✗ Source test failed with code: {e.code}")
except Exception as e:
    print(f"\n✗ Error testing source: {e}")

input("\nPress Enter to continue...")
```

**Terminal Output:**
```
  Select source to test:
  > Hacker News
    Lobsters
    BBC News
    Back

--- Testing Source: hn ---
Fetching 3 articles...

Processing hn articles...
[Article processing output...]
Successfully processed 3 articles

[OK] Source 'hn' test completed

Press Enter to continue...
```

## Main Menu Handlers

### _handle_bundle_flow()
Location: Application/core/interactive.py:436

**Purpose:** Handle bundle selection and execution.

**Workflow:**

**Step 1: Menu Positioning**
```python
# Bundle menu can be long
position_menu_at_bottom(menu_lines=15)
```

**Step 2: Bundle Discovery**
```python
from cli import get_available_bundles, get_available_sources
from core.source_system.source_registry import get_source_registry

bundles = get_available_bundles()
all_sources_map = get_available_sources()
registry = get_source_registry()
```

**Step 3: Bundle Choices Construction**
```python
bundle_choices = []

for name, data in bundles.items():
    description = data.get("description", "")

    # Special handling for 'all' bundle
    if name == "all":
        full_description = description
    else:
        # Explicit sources from bundles.yml
        bundle_sources = data.get("sources", [])

        # Auto-discover sources with matching category
        category_sources = registry.get_sources_by_category(name)
        for source_id in category_sources:
            if source_id not in bundle_sources:
                bundle_sources.append(source_id)

        # Format with source names
        source_names = [all_sources_map.get(sid, sid) for sid in bundle_sources]
        sources_str = f"\n   ({', '.join(source_names)})" if source_names else ""
        full_description = f"{description}{sources_str}"

    bundle_choices.append(questionary.Choice(f"{name} - {full_description}", name))
```

**Step 4: Interactive Selection**
```python
bundle = questionary.select(
    "  Select a news bundle and hit Enter for activation.",
    choices=bundle_choices,
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use arrow keys to navigate)",
).ask()
```

**Step 5: HTML Prompt**
```python
if bundle and bundle != 'back':
    _prompt_for_html('bundle', bundle)
```

**Terminal Output:**
```
  Select a news bundle and hit Enter for activation.

  > tech - Technology News
   (IEEE Spectrum, Mashable, Gizmodo)

    techpro - Advanced Technology
   (Hacker News, Lobsters, InfoQ)

    news - General News
   (BBC News, The Guardian)

    science - Science News
   (Nature News, Scientific American)

    all - All available sources

    Back to Main Menu

   (Use arrow keys to navigate)
```

### _handle_fetch_flow()
Location: Application/core/interactive.py:492

**Purpose:** Handle multi-source selection and execution.

**Workflow:**

**Step 1: Menu Positioning**
```python
position_menu_at_bottom(menu_lines=15)
```

**Step 2: Source Choices**
```python
from cli import get_available_sources
sources = get_available_sources()

source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
source_choices.append(questionary.Separator())
source_choices.append(questionary.Choice("Back to Main Menu", "back"))
```

**Step 3: Checkbox Selection**
```python
selected_sources = questionary.checkbox(
    "  Select sources (Space to select, Enter to confirm):",
    choices=source_choices,
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use Space to select multiple sources, Enter to confirm)",
).ask()
```

**Checkbox Navigation:**
- Arrow keys: Move between sources
- Space: Toggle selection (checkbox)
- Enter: Confirm all selected
- Ctrl+C: Cancel

**Step 4: HTML Prompt**
```python
if selected_sources and 'back' not in selected_sources:
    _prompt_for_html('fetch', selected_sources)
```

**Terminal Output:**
```
  Select sources (Space to select, Enter to confirm):

  [ ] hn              Hacker News
  [x] lb              Lobsters
  [x] iq              InfoQ
  [ ] bbc             BBC News
  [ ] guardian        The Guardian

  Back to Main Menu

   (Use Space to select multiple sources, Enter to confirm)
```

### _handle_single_source_flow()
Location: Application/core/interactive.py:520

**Purpose:** Handle single source selection and execution.

**Workflow:**

**Step 1: Menu Positioning**
```python
position_menu_at_bottom(menu_lines=15)
```

**Step 2: Source Selection**
```python
from cli import get_available_sources
sources = get_available_sources()

source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
source_choices.append(questionary.Separator())
source_choices.append(questionary.Choice("Back to Main Menu", "back"))

source = questionary.select(
    "  Select a source and hit Enter for activation.",
    choices=source_choices,
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use arrow keys to navigate)",
).ask()
```

**Step 3: HTML Prompt**
```python
if source and source != 'back':
    # For single source, call fetch with just one source
    _prompt_for_html('fetch', [source])
```

**Note:** Internally uses `fetch` action with single-item list, not separate `single_source` action.

### _handle_single_url_flow()
Location: Application/core/interactive.py:549

**Purpose:** Handle single article URL input and execution.

**Workflow:**

**Step 1: Menu Positioning**
```python
position_menu_at_bottom(menu_lines=5)
```

**Step 2: URL Input**
```python
print("  (Use Ctrl+C to go to the Main Menu)")

url = questionary.text(
    "  Please enter the article URL:",
    style=custom_style,
    qmark="",
).ask()
```

**Step 3: Validation**
```python
if url:
    _prompt_for_html('single', url)
else:
    repeat = questionary.confirm(
        "  No URL entered. Would you like to try again?",
        default=True,
        style=custom_style,
        qmark="",
    ).ask()

    if repeat:
        _handle_single_url_flow()  # Recursive call
```

**Terminal Output:**
```
  (Use Ctrl+C to go to the Main Menu)
  Please enter the article URL: https://example.com/article

[Proceeds to HTML prompt]
```

**Empty Input Handling:**
```
  Please enter the article URL: [Enter pressed]

  No URL entered. Would you like to try again? Yes

  Please enter the article URL:
```

## Shared Functions

### _prompt_for_html(action, selection)
Location: Application/core/interactive.py:578

**Purpose:** Prompt user for HTML generation preference.

**Parameters:**
- `action` (str) - Action type: 'bundle', 'fetch', or 'single'
- `selection` - Bundle name, source list, or URL depending on action

**Workflow:**

**Step 1: Menu Positioning**
```python
position_menu_at_bottom(menu_lines=8)
```

**Step 2: HTML Prompt**
```python
response = questionary.select(
    "  Generate HTML for web browsing?",
    choices=[
        questionary.Choice("Yes", "yes"),
        questionary.Choice("No", "no"),
        questionary.Separator(),
        questionary.Choice("Back to Main Menu", "back"),
    ],
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n   (Use arrow keys to navigate)",
).ask()
```

**Step 3: Execution**
```python
if response and response != 'back':
    generate_html = response == "yes"
    _confirm_and_execute(action, selection, generate_html)
```

**Terminal Output:**
```
  Generate HTML for web browsing?

  > Yes
    No

    Back to Main Menu

   (Use arrow keys to navigate)
```

### _confirm_and_execute(action, selection, generate_html)
Location: Application/core/interactive.py:604

**Purpose:** Display summary and execute command via run_app().

**Parameters:**
- `action` (str) - Action type: 'bundle', 'fetch', or 'single'
- `selection` - Action-specific data
- `generate_html` (bool) - HTML generation flag

**Workflow:**

**Step 1: Summary Construction**
```python
summary = f"Action: {action}\n"

if action == 'bundle':
    summary += f"Bundle: {selection}\n"
elif action == 'fetch':
    summary += f"Sources: {', '.join(selection)}\n"
elif action == 'single':
    summary += f"URL: {selection}\n"

summary += f"Generate HTML: {generate_html}\n"
```

**Step 2: Summary Display**
```python
print("--------------------")
print("SUMMARY")
print(summary)
print("--------------------")
```

**Step 3: Argument Construction**
```python
args = [action]

if action == 'bundle':
    args.append(selection)
elif action == 'fetch':
    args.append(','.join(selection))
elif action == 'single':
    args.append(selection)

if generate_html:
    args.append('--html')
```

**Step 4: Execution**
```python
try:
    print("Executing command...")
    run_app(args)  # From Application/capcat.py:run_app()
except SystemExit as e:
    if e.code != 0:
        print(f"Command finished with error code: {e.code}")
        sys.exit(e.code)  # Re-raise error for wrapper
    # On success (code 0), continue without exiting
```

**Step 5: Return to Menu**
```python
input("\nPress Enter to return to main menu...")
```

**Terminal Output:**
```
--------------------
SUMMARY
Action: bundle
Bundle: tech
Generate HTML: true
--------------------

Executing command...

Processing ieee articles...
Processing mashable articles...
[Article processing output...]

Successfully processed 2 sources

Press Enter to return to main menu...
```

## Bundle Management

### _handle_manage_bundles()
Location: Application/core/interactive.py:649

**Purpose:** Handle bundle management submenu.

**Workflow:**

**Step 1: Service Initialization**
```python
from pathlib import Path
from core.source_system.bundle_service import BundleService

bundles_path = Path(__file__).parent.parent / "sources" / "active" / "bundles.yml"
service = BundleService(bundles_path)
```

**Step 2: Menu Loop**
```python
while True:
    action = service.ui.show_bundle_menu()

    if not action or action == 'back':
        return

    # Execute action
    if action == 'create':
        service.execute_create_bundle()
    elif action == 'edit':
        service.execute_edit_bundle()
    elif action == 'delete':
        service.execute_delete_bundle()
    elif action == 'add_sources':
        service.execute_add_sources()
    elif action == 'remove_sources':
        service.execute_remove_sources()
    elif action == 'move_sources':
        service.execute_move_source()
    elif action == 'list':
        service.execute_list_bundles()
```

**Available Actions:**
- `create` - Create new bundle
- `edit` - Edit bundle name/description
- `delete` - Delete bundle
- `add_sources` - Add sources to bundle
- `remove_sources` - Remove sources from bundle
- `move_sources` - Move sources between bundles
- `list` - List all bundles

**Service Location:** Application/core/source_system/bundle_service.py

## Integration with CLI

### run_app() Integration
Location: Application/capcat.py

**How Interactive Mode Calls CLI:**

```python
from capcat import run_app

# Example: Bundle execution
args = ['bundle', 'tech', '--html']
run_app(args)
```

**Arguments Format:**
```python
# Bundle
args = ['bundle', bundle_name, '--html']  # or without --html

# Fetch
args = ['fetch', 'source1,source2,source3', '--html']

# Single
args = ['single', url, '--html']
```

**Exit Code Handling:**
```python
try:
    run_app(args)
except SystemExit as e:
    if e.code != 0:
        # Handle error
        print(f"Error: {e.code}")
        sys.exit(e.code)  # Re-raise for wrapper
    # Success: Continue interactive mode
```

**Why SystemExit:** `run_app()` calls `sys.exit()` on completion, which raises `SystemExit` exception. Interactive mode catches this to prevent exiting.

## Error Handling

### Network Errors
```python
try:
    run_app(args)
except SystemExit as e:
    if e.code != 0:
        print(f"Command finished with error code: {e.code}")
```

### User Cancellation
```python
if response is None:  # User pressed Ctrl+C
    return  # Go back to previous menu
```

### Invalid Input
```python
if not url:
    print("  No URL provided. Returning to menu.")
    return
```

### Service Errors
```python
except Exception as e:
    print(f"Error: {e}")
    input("\nPress Enter to continue...")
```

## Keyboard Navigation

### All Menus
- **Arrow Up/Down:** Navigate options
- **Enter:** Confirm selection
- **Ctrl+C:** Cancel/go back
- **Escape:** Same as Ctrl+C

### Checkbox Menus (Multi-select)
- **Space:** Toggle selection
- **Arrow Up/Down:** Navigate
- **Enter:** Confirm all selected
- **Ctrl+C:** Cancel

### Text Input
- **Type:** Enter text
- **Backspace:** Delete character
- **Ctrl+U:** Clear entire line
- **Enter:** Confirm input
- **Ctrl+C:** Cancel input

## Session Management

### State Persistence
- **No persistent state:** Each operation is independent
- **No session history:** Previous selections not remembered
- **Fresh state:** Each menu start is clean

### Configuration
- **Uses global config:** `capcat.yml` and environment variables
- **No interactive-specific config:** Same settings as CLI

## Source Code Locations

Function reference:
- `start_interactive_mode()` - Application/core/interactive.py:78
- `position_menu_at_bottom()` - Application/core/interactive.py:39
- `suppress_logging()` - Application/core/interactive.py:28
- `_handle_manage_sources_flow()` - Application/core/interactive.py:132
- `_handle_bundle_flow()` - Application/core/interactive.py:436
- `_handle_fetch_flow()` - Application/core/interactive.py:492
- `_handle_single_source_flow()` - Application/core/interactive.py:520
- `_handle_single_url_flow()` - Application/core/interactive.py:549
- `_prompt_for_html()` - Application/core/interactive.py:578
- `_confirm_and_execute()` - Application/core/interactive.py:604
- `_show_source_details()` - Application/core/interactive.py:351

## Related Documentation

- CLI Commands: docs/tutorials/01-cli-commands-exhaustive.md
- Source System: docs/tutorials/04-source-system-exhaustive.md
- Configuration: docs/tutorials/03-configuration-exhaustive.md
