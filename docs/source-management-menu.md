# Source Management Interactive Menu

The source management menu provides a user-friendly interface for adding, removing, and configuring news sources in Capcat.

This is a submenu within Capcat's interactive mode. For complete interactive mode documentation, see [Interactive Mode Guide](interactive-mode.html).

## Accessing the Menu

Launch the interactive menu:

```bash
./capcat catch
```

From the main menu, select **"Manage Sources (add/remove/configure)"** to access the source management submenu.

## Menu Options

### 1. Add New Source from RSS Feed

Quickly add a new source by providing an RSS feed URL.

**Flow:**
1. Enter RSS feed URL
2. System inspects feed and extracts metadata
3. Choose source ID (auto-suggested from feed title)
4. Select category (tech, news, science, ai, sports, etc.)
5. Optionally add to a bundle
6. Optionally test the new source

**Example:**
```
Enter the RSS feed URL: https://techcrunch.com/feed/

[OK] Feed 'TechCrunch' found.

Source ID: techcrunch
Category: tech
Add to bundle? Yes
  Select bundle: tech
[OK] Added 'techcrunch' to bundle 'tech'.

Test fetch? Yes
[OK] Source added and verified successfully!
```

### 2. Generate Custom Source Config

Create a comprehensive YAML configuration for more complex sources.

**Features:**
- Interactive prompts for all configuration options
- Discovery method selection (RSS or HTML scraping)
- Custom selectors for article and content extraction
- Image processing configuration
- Rate limiting and timeout settings
- URL skip patterns
- Template configuration

**What you configure:**
- Source ID and display name
- Category
- Base URL
- Discovery method (RSS feed URL or HTML selectors)
- Article link selectors
- Content extraction selectors
- Image processing rules
- Request timeout and rate limiting
- Skip patterns (URLs to avoid)

**Output:**
A complete YAML file saved to `sources/active/config_driven/configs/`

### 3. Remove Existing Sources

Interactive source removal with safety features.

**Features:**
- Select multiple sources for removal
- Automatic backup before removal
- Usage analytics display
- Dry-run mode available (via CLI)
- Undo capability

**Flow:**
1. View list of available sources with usage stats
2. Select sources to remove
3. Review changes
4. Confirm removal
5. Backup created automatically
6. Sources removed from:
   - Configuration files
   - Bundle definitions
   - Registry cache

**Safety:**
- Backups stored in `.capcat-backups/`
- Can undo last removal
- Confirmation required

### 4. List All Sources

View all available sources grouped by category.

**Display Format:**
```
TECH:
  - hn             Hacker News
  - lb             Lobsters
  - iq             InfoQ
  - gizmodo        Gizmodo

NEWS:
  - bbc            BBC News
  - guardian       The Guardian

SCIENCE:
  - nature         Nature News
  - scientificamerican Scientific American

Total: 15 sources
```

### 5. Test a Source

Validate that a source is working correctly.

**Flow:**
1. Select source from list
2. System fetches 3 sample articles
3. Results displayed
4. Success/failure indication

**Use Cases:**
- Verify new source works
- Check if existing source still functions
- Troubleshoot source issues
- Validate configuration changes

### 6. Back to Main Menu

Return to the main Capcat catch menu.

## Usage Examples

### Add a New Tech Blog

```bash
./capcat catch
> Manage Sources (add/remove/configure)
> Add New Source from RSS Feed

  Enter RSS feed URL: https://arstechnica.com/feed/

[OK] Feed 'Ars Technica' found.
Source ID: arstechnica
Category: tech
Add to bundle? Yes
  Bundle: tech
Test fetch? Yes
[OK] Source added successfully!
```

### Remove Outdated Sources

```bash
./capcat catch
> Manage Sources (add/remove/configure)
> Remove Existing Sources

Select sources to remove:
  [x] oldblog
  [x] discontinued-source
  [ ] current-source

Confirm removal? Yes
[OK] Backup created: .capcat-backups/backup_20251019_143022/
[OK] 2 sources removed successfully
```

### Create Complex Custom Source

```bash
./capcat catch
> Manage Sources (add/remove/configure)
> Generate Custom Source Config

[Interactive configuration wizard launches]
- Source ID: newsite
- Display name: NewSite Tech
- Category: tech
- Discovery method: html
- Article selectors: h2.headline a
- Content selectors: div.article-content
- Images: article img
- Rate limit: 5 seconds
...

Configuration saved to: sources/active/config_driven/configs/newsite.yaml

Next steps:
1. Review: cat sources/active/config_driven/configs/newsite.yaml
2. Test: ./capcat fetch newsite --count 5
3. Add to bundle: edit sources/active/bundles.yml
```

## CLI Equivalents

All menu functions have CLI equivalents:


- **Add New Source from RSS** → `./capcat add-source --url <url>`
- **Generate Custom Config** → `./capcat generate-config`
- **Remove Sources** → `./capcat remove-source`
- **List All Sources** → `./capcat list sources`
- **Test a Source** → `./capcat fetch <source-id> --count 3`

## Integration with Existing Workflows

### After Adding a Source

1. **Test it**: Use "Test a Source" option
2. **Add to bundle**: Automatically prompted during add
3. **Fetch articles**: Return to main menu and use new source

### Before Removing a Source

1. **Check usage**: Analytics shown during removal
2. **Backup created**: Automatic safety net
3. **Can undo**: Use `./capcat remove-source --undo`

## Tips

### Quick Add Workflow

For adding multiple RSS sources quickly:
1. Prepare list of RSS URLs
2. Use menu for first source (sets pattern)
3. Subsequent sources follow same category/bundle

### Testing Configuration Changes

After modifying a config file:
1. Use "Test a Source" to validate
2. Check output quality
3. Adjust selectors if needed
4. Re-test until satisfied

### Managing Many Sources

1. Use "List All Sources" to audit
2. Group by category
3. Remove unused sources periodically
4. Keep configurations up to date

## Troubleshooting

### "Source not found" after adding

- Check config file was created
- Verify YAML syntax is valid
- Restart Capcat to reload registry

### Test fetch fails

- Verify RSS URL is accessible
- Check network connectivity
- Review error messages
- Try reducing count to 1

### Cannot remove source

- Check source isn't in use
- Verify write permissions
- Review error output
- Try with backup disabled

## Advanced Features

### Batch Operations

Use CLI for batch operations:
```bash
# Add multiple sources from file
./capcat add-source --batch sources.txt

# Remove multiple sources
./capcat remove-source --batch remove-list.txt
```

### Backup Management

Backups stored in `.capcat-backups/`:
```bash
# List backups
ls -la .capcat-backups/

# Restore specific backup
./capcat remove-source --undo backup_20251019_143022

# Restore last backup
./capcat remove-source --undo
```

### Custom Configurations

Edit configs manually:
```bash
# Open config in editor
vim sources/active/config_driven/configs/newsource.yaml

# Validate syntax
python3 -c "import yaml; yaml.safe_load(open('newsource.yaml'))"

# Test changes
./capcat fetch newsource --count 3
```

## See Also

- [Interactive Mode Guide](interactive-mode.html) - Complete interactive menu documentation
- [Quick Start Guide](quick-start.html) - Getting started with Capcat
- [Source Development Guide](source-development.html) - Creating custom sources
- [Dependency Management](dependency-management.html) - Troubleshooting issues
- [Architecture](architecture.html) - How source system works

## Keyboard Shortcuts

- **Arrow keys**: Navigate menu options
- **Enter**: Select option
- **Space**: Select/deselect (checkboxes)
- **Ctrl+C**: Go back / cancel operation
- **Tab**: Autocomplete (text input)

## Best Practices

1. **Test before deploying**: Always test new sources
2. **Use meaningful IDs**: Choose clear, lowercase source IDs
3. **Categorize correctly**: Helps with bundle organization
4. **Regular audits**: Remove unused sources
5. **Backup before bulk changes**: Use dry-run first
6. **Document custom sources**: Add comments to YAML configs

---

The source management menu makes it easy to maintain your Capcat news sources without touching configuration files directly. All operations are interactive, safe, and reversible.
