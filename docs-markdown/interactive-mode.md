# Interactive Mode Guide

Capcat's interactive mode provides a user-friendly menu interface for all operations without requiring command-line arguments or flags.

## Quick Start

Launch interactive mode:

```bash
./capcat catch
```

## Main Menu

When you launch `./capcat catch`, you see:

```
  What would you like me to do?

  > Catch articles from a bundle of sources
    Catch articles from a list of sources
    Catch from a single source
    Catch a single article by URL
    Manage Sources (add/remove/configure)
    Exit

   (Use arrow keys to navigate)
```

**Navigation:**
- Arrow keys: Move between options
- Enter: Select option
- Ctrl+C: Exit at any time

## Main Menu Options

### 1. Catch Articles from a Bundle

Fetch articles from predefined source groups.

**Flow:**
1. Select bundle (tech, news, science, ai, sports)
2. Choose HTML generation (yes/no)
3. Confirm and execute

**Example:**
```
  Select a news bundle and hit Enter for activation.

  > tech - Technology News
    (IEEE, Mashable)

    news - General News
    (BBC News, The Guardian)

    science - Science News
    (Nature News, Scientific American)

    ai - AI & Machine Learning
    (MIT News)

    sports - Sports News
    (BBC Sport)
```

**Bundle Auto-Discovery:**
Bundles automatically include:
- Sources explicitly listed in `bundles.yml`
- Sources with matching category from registry
- Example: "tech" bundle includes all sources with `category: tech`

**Default Count:**
- Bundles fetch default number of articles per source (typically 30)
- Cannot be changed interactively (use CLI for custom counts)

### 2. Catch Articles from a List of Sources

Select multiple sources to fetch from simultaneously.

**Flow:**
1. Select sources with spacebar (checkbox mode)
2. Press Enter to confirm selection
3. Choose HTML generation
4. Execute

**Example:**
```
  Select sources with <space> and press Enter to continue:

  [ ] hn              Hacker News
  [x] lb              Lobsters
  [x] iq              InfoQ
  [ ] bbc             BBC News
  [ ] guardian        The Guardian

   (Use <space> to select, <enter> to confirm)
```

**Tips:**
- Select as many sources as needed
- Sources are grouped by category for easy browsing
- No limit on number of selections

### 3. Catch from a Single Source

Fetch articles from one specific source.

**Flow:**
1. Select source from list
2. Choose HTML generation
3. Execute

**Example:**
```
  Select a source and hit Enter for activation.

  > hn              Hacker News
    lb              Lobsters
    iq              InfoQ
    bbc             BBC News
    guardian        The Guardian
```

**Use Case:**
Testing a specific source or fetching focused content.

### 4. Catch a Single Article by URL

Download and convert a single article from any URL.

**Flow:**
1. Enter article URL
2. Choose HTML generation
3. Execute

**Example:**
```
  (Use Ctrl+C to go to the Main Menu)

  Please enter the article URL: https://example.com/article

  Generate HTML for web browsing?
  > Yes
    No
```

**Supported:**
- Any publicly accessible article URL
- Works with sources not in registry
- Automatic content extraction
- Media download (images always, videos/docs with --media flag)

### 5. Manage Sources (add/remove/configure)

Enter source management submenu.

See [Source Management Submenu](#source-management-submenu) section below.

### 6. Exit

Leave interactive mode and return to shell.

## Source Management Submenu

Accessed via "Manage Sources" from main menu.

```
  Source Management - Select an option:

  > Add New Source from RSS Feed
    Generate Custom Source Config
    Remove Existing Sources
    List All Sources
    Test a Source
    ────────────────
    Back to Main Menu

   (Use arrow keys to navigate)
```

### Add New Source from RSS Feed

Quick source addition from RSS/Atom feeds.

**Flow:**
1. Enter RSS feed URL
2. System inspects feed and extracts metadata
3. Review auto-suggested source ID
4. Select category
5. Optionally add to bundle
6. Optionally test source

**Example:**
```
  Enter the RSS feed URL: https://example.com/article

[OK] Feed 'TechCrunch' found.

Source ID: techcrunch
Category: tech
Add to bundle? Yes
  Select bundle: tech
[OK] Added 'techcrunch' to bundle 'tech'.

Test fetch? Yes
[OK] Source added and verified successfully!
```

**What It Creates:**
- YAML config in `sources/active/config_driven/configs/`
- Registry entry (automatic on next run)
- Bundle entry (if selected)

### Generate Custom Source Config

Create comprehensive YAML configuration with all options.

**Flow:**
1. Interactive wizard with detailed prompts
2. Configure all source parameters
3. YAML file generated and saved
4. Instructions provided for testing

**Configurable Options:**
- Source ID and display name
- Category (tech, news, science, ai, sports, other)
- Base URL
- Discovery method (RSS feed or HTML scraping)
- Article link selectors (CSS/XPath)
- Content extraction selectors
- Image processing rules
- Author/date extraction patterns
- Rate limiting (seconds between requests)
- Request timeout
- Skip patterns (URLs to avoid)
- Template selection

**Output Location:**
```
sources/active/config_driven/configs/sourceid.yaml
```

**Next Steps:**
```bash
# Review configuration
cat sources/active/config_driven/configs/newsource.yaml

# Test source
./capcat fetch newsource --count 5

# Add to bundle (edit bundles.yml)
vim sources/active/bundles.yml
```

### Remove Existing Sources

Interactive source removal with safety features.

**Flow:**
1. View list of available sources with usage stats
2. Select sources to remove (checkbox mode)
3. Review changes
4. Confirm removal
5. Automatic backup created
6. Sources removed from all locations

**Safety Features:**
- Automatic backup to `.capcat-backups/`
- Usage analytics displayed
- Confirmation required
- Undo capability available

**What Gets Removed:**
- Config files (`sources/active/config_driven/configs/` or `sources/active/custom/`)
- Bundle definitions (from `bundles.yml`)
- Registry cache

**Backup Structure:**
```
.capcat-backups/
└── backup_YYYYMMDD_HHMMSS/
    ├── configs/
    ├── bundles.yml
    └── manifest.json
```

**Undo Last Removal:**
```bash
./capcat remove-source --undo
```

### List All Sources

Display all available sources grouped by category.

**Output Format:**
```
--- Available Sources ---

TECH:
  - ieee           IEEE Spectrum
  - mashable       Mashable

TECHPRO:
  - hn             Hacker News
  - lb             Lobsters
  - iq             InfoQ

NEWS:
  - bbc            BBC News
  - guardian       The Guardian

SCIENCE:
  - nature         Nature News
  - scientificamerican Scientific American

AI:
  - mitnews        MIT News

SPORTS:
  - bbcsport       BBC Sport

Total: 11 sources
```

**Use Cases:**
- Audit available sources
- Find source IDs for CLI commands
- Check categorization
- Identify gaps in coverage

### Test a Source

Validate source functionality by fetching sample articles.

**Flow:**
1. Select source from list
2. System fetches 3 test articles
3. Results displayed
4. Success/failure indication

**Example:**
```
--- Testing Source: hn ---
Fetching 3 articles...

[OK] Article 1: "New AI Model Released"
[OK] Article 2: "Programming Best Practices"
[OK] Article 3: "Tech Industry Trends"

[OK] Source 'hn' test completed
```

**Use Cases:**
- Verify new source works
- Troubleshoot source issues
- Check after configuration changes
- Validate after website updates

**What It Tests:**
- Network connectivity
- Article discovery
- Content extraction
- Media download
- Markdown conversion

## HTML Generation

All main operations prompt for HTML generation.

**Options:**
- **Yes**: Generate browsable HTML with styling
- **No**: Markdown only

**HTML Output:**
```
Article_Folder/
├── article.md       # Always created
├── comments.md      # If source supports comments
├── images/          # Downloaded media
└── html/           # Only if HTML enabled
    ├── article.html
    └── comments.html
```

**When to Use HTML:**
- Web browsing convenience
- Sharing with non-technical users
- Visual verification
- Archival with styling

**When to Skip:**
- CLI-only workflows
- Minimal disk usage
- Processing with markdown tools
- Speed optimization

## Execution Summary

Before execution, interactive mode shows a summary:

```
--------------------
SUMMARY
Action: bundle
Bundle: tech
Generate HTML: true
--------------------

Executing command...
```

**What Happens:**
1. Arguments validated
2. Sources initialized
3. Articles fetched
4. Content processed
5. Media downloaded
6. Files written
7. HTML generated (if enabled)
8. Success confirmation

**Return to Menu:**
After execution completes, press Enter to return to main menu.

## CLI Equivalents

All interactive operations have CLI equivalents:

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Interactive Option</th>
      <th>CLI Command</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Bundle</td>
      <td><code>./capcat bundle tech --count 30</code></td>
    </tr>
    <tr>
      <td>List of sources</td>
      <td><code>./capcat fetch hn,bbc --count 30</code></td>
    </tr>
    <tr>
      <td>Single source</td>
      <td><code>./capcat fetch hn --count 30</code></td>
    </tr>
    <tr>
      <td>Single URL</td>
      <td><code>./capcat single https://example.com/article</code></td>
    </tr>
    <tr>
      <td>Add RSS source</td>
      <td><code>./capcat add-source --url <url></code></td>
    </tr>
    <tr>
      <td>Generate config</td>
      <td><code>./capcat generate-config</code></td>
    </tr>
    <tr>
      <td>Remove sources</td>
      <td><code>./capcat remove-source</code></td>
    </tr>
    <tr>
      <td>List sources</td>
      <td><code>./capcat list sources</code></td>
    </tr>
    <tr>
      <td>Test source</td>
      <td><code>./capcat fetch <source> --count 3</code></td>
    </tr>
  </tbody>
</table>
</div>

**CLI Advantages:**
- Custom count values
- Scriptable
- Automation-friendly
- Advanced flags (`--media`, `--verbose`, `-L`)

**Interactive Advantages:**
- No flag memorization
- Guided workflows
- Visual feedback
- Error prevention

## Advanced Features

### Screen Management

Interactive mode automatically:
- Clears screen between menus
- Maintains clean display
- Shows selected options
- Hides logging noise

### Logging Suppression

During menu navigation, logging is suppressed to prevent clutter.

**When Active:**
- Showing menus
- Collecting input
- Navigation

**When Disabled:**
- During execution
- Error messages
- Progress updates

### Session Continuity

After each operation:
- Return to main menu
- Previous selections not remembered
- Fresh state each time
- No persistent session

### Error Handling

Errors display helpful messages:

```
Error adding source: Invalid RSS feed URL

Press Enter to continue...
```

**Recovery:**
- Returns to menu
- No data loss
- Can retry operation
- Clear error description

## Keyboard Shortcuts

**Universal:**
- Arrow keys: Navigate options
- Enter: Confirm selection
- Ctrl+C: Cancel/go back
- Space: Toggle checkbox (multi-select)

**Text Input:**
- Tab: Autocomplete (if available)
- Backspace: Delete character
- Ctrl+U: Clear line
- Ctrl+C: Cancel input

## Best Practices

### For New Users

1. Start with **"List All Sources"** to see what's available
2. Test with **"Catch from a single source"** first
3. Use **bundles** once comfortable
4. Enable **HTML generation** for visual verification

### For Source Management

1. Always **test after adding** a source
2. Use **meaningful source IDs** (lowercase, no spaces)
3. **Categorize correctly** for bundle auto-discovery
4. **Remove unused sources** periodically

### For Daily Use

1. **Bundles** for routine fetching
2. **List of sources** for custom combinations
3. **Single URL** for ad-hoc articles
4. **Test source** before reporting issues

## Troubleshooting

### Menu Not Appearing

```bash
# Check wrapper system
./capcat --help

# Try Python wrapper directly
python3 run_capcat.py catch

# Check dependencies
source venv/bin/activate
python -c "import questionary"
```

### Selection Not Working

- Ensure terminal supports ANSI codes
- Check keyboard/terminal compatibility
- Try different terminal emulator
- Use CLI commands as fallback

### Source Not Listed

**After adding a source:**
1. Check config file was created
2. Verify YAML syntax (no tabs, proper indentation)
3. Restart Capcat to reload registry
4. Check error messages in logs

**For existing sources:**
1. Run `./capcat list sources`
2. Check if source was removed
3. Verify source directory structure
4. Review registry discovery logs

### Test Fetch Fails

**Common Causes:**
- Network connectivity issues
- Website structure changed
- Anti-bot protection
- Invalid selectors
- Rate limiting

**Debugging:**
```bash
# Detailed logging
./capcat -V fetch sourceid --count 3

# Check configuration
cat sources/active/config_driven/configs/sourceid.yaml

# Manual test
curl -I https://source-url.com
```

## Integration with Workflows

### Development Workflow

```bash
# 1. Add new source interactively
./capcat catch
  > Manage Sources
  > Add New Source from RSS Feed

# 2. Test thoroughly
./capcat catch
  > Manage Sources
  > Test a Source

# 3. Use in production
./capcat bundle tech --count 50
```

### Content Curation Workflow

```bash
# Morning routine
./capcat catch
  > Catch articles from a bundle
  > tech
  > Yes (HTML)

# Ad-hoc interesting article
./capcat catch
  > Catch a single article by URL
  > [paste URL]
```

### Maintenance Workflow

```bash
# Weekly audit
./capcat catch
  > Manage Sources
  > List All Sources

# Remove outdated
./capcat catch
  > Manage Sources
  > Remove Existing Sources

# Verify remaining
./capcat catch
  > Manage Sources
  > Test a Source
```

## Implementation Details

### Technology Stack

- **UI Framework**: questionary (prompt_toolkit)
- **Styling**: Custom ANSI color scheme (orange theme)
- **Screen Control**: ANSI escape codes
- **Input Handling**: Arrow keys, space, enter

### Code Structure

```
core/
└── interactive.py                    # Main interactive module
    ├── start_interactive_mode()      # Main menu loop
    ├── _handle_bundle_flow()         # Bundle selection
    ├── _handle_fetch_flow()          # Multi-source selection
    ├── _handle_single_source_flow()  # Single source selection
    ├── _handle_single_url_flow()     # URL input
    ├── _handle_manage_sources_flow() # Source management submenu
    ├── _handle_add_source_from_rss() # RSS source addition
    ├── _handle_generate_config()     # Config generator
    ├── _handle_remove_source()       # Source removal
    ├── _handle_list_sources()        # Source listing
    ├── _handle_test_source()         # Source testing
    ├── _prompt_for_html()            # HTML generation prompt
    └── _confirm_and_execute()        # Execution handler
```

### Color Scheme

```python
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer
    ('answer', 'fg:#d75f00'),            # Orange answer
])
```

### Integration Points

**With CLI:**
- Uses same `run_app()` function
- Constructs argument list programmatically
- Handles `SystemExit` exceptions

**With Core:**
- Imports from `cli` module
- Uses `get_available_sources()`
- Uses `get_available_bundles()`
- Integrates with source registry

**With Source System:**
- Source management commands
- Registry operations
- Backup manager
- Analytics system

## Comparison: Interactive vs CLI

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Interactive</th>
      <th>CLI</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Learning Curve</td>
      <td>Low</td>
      <td>Medium</td>
    </tr>
    <tr>
      <td>Speed</td>
      <td>Moderate</td>
      <td>Fast</td>
    </tr>
    <tr>
      <td>Scriptable</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Custom Counts</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Media Flag</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Error Prevention</td>
      <td>High</td>
      <td>Low</td>
    </tr>
    <tr>
      <td>Visual Feedback</td>
      <td>Excellent</td>
      <td>Basic</td>
    </tr>
    <tr>
      <td>Automation</td>
      <td>Not suitable</td>
      <td>Ideal</td>
    </tr>
    <tr>
      <td>Documentation Needed</td>
      <td>Minimal</td>
      <td>Extensive</td>
    </tr>
    <tr>
      <td>New User Friendly</td>
      <td>Yes</td>
      <td>No</td>
    </tr>
  </tbody>
</table>
</div>

**Recommendation:**
- **Interactive**: Daily use, source management, new users
- **CLI**: Scripts, custom parameters, advanced users, automation

## See Also

- [Source Management Menu](source-management-menu.html) - Detailed source management docs
- [Quick Start Guide](quick-start.html) - Getting started with Capcat
- [Source Development](source-development.html) - Creating custom sources
- [CLI Reference](tutorials/01-cli-commands-exhaustive.html) - All CLI commands
- [Architecture](architecture.html) - System design

## Future Enhancements

Potential additions to interactive mode:

- Custom count selection in bundles
- Media flag toggle
- Verbose output option
- Configuration editing
- Bundle creation/editing
- Source statistics dashboard
- Scheduling interface
- Export/import configurations

---

Interactive mode makes Capcat accessible to users of all skill levels while maintaining full power for advanced users through CLI commands.
