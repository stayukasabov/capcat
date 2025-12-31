# Interactive Mode Guide

Use Capcat's visual menu system for zero-memorization operation.

## What You'll Learn

- Launch and navigate interactive mode
- Use the main menu
- Manage sources visually
- Quick operations without typing commands

## Starting Interactive Mode

```bash
./capcat catch
```

You'll see the Capcat logo and main menu:

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

## Navigation Basics

**Arrow Keys:** Move up/down through options
**Enter:** Select highlighted option
**Ctrl+C:** Go back to previous menu
**Space:** Toggle checkboxes (when selecting multiple items)

## Main Menu Options

### 1. Catch from a Bundle

**What it does:** Fetch from pre-configured source groups

**Steps:**
1. Select "Catch articles from a bundle of sources"
2. Choose your bundle (tech, news, science, etc.)
3. Choose whether to generate HTML
4. Articles are fetched automatically

**Example:**
```
Select: tech
Generate HTML: Yes
Action: bundle
Bundle: tech
Generate HTML: true
```

**Result:** Tech news collected with HTML for browsing

### 2. Catch from Multiple Sources

**What it does:** Pick individual sources to fetch from

**Steps:**
1. Select "Catch articles from a list of sources"
2. Use Space to check sources you want
3. Press Enter when done selecting
4. Choose HTML generation
5. Articles are fetched

**Example:**
Select with Space:
```
[x] hn              Hacker News
[x] bbc             BBC News
[ ] guardian        The Guardian
[x] nature          Nature News
```

**Result:** Articles from HN, BBC, and Nature

### 3. Catch from Single Source

**What it does:** Fetch from one source only

**Steps:**
1. Select "Catch from a single source"
2. Choose the source from the list
3. Choose HTML generation
4. Articles are fetched

**Faster than:** Typing `./capcat fetch sourcename`

### 4. Catch Single Article by URL

**What it does:** Download one specific article

**Steps:**
1. Select "Catch a single article by URL"
2. Paste the article URL
3. Choose HTML generation
4. Article is saved

**Use case:** Found an interesting article while browsing

### 5. Manage Sources

Opens the source management submenu:

```
Source Management - Select an option:

  > Add New Source from RSS Feed
    Generate Custom Source Config
    Remove Existing Sources
    List All Sources
    Test a Source
    Manage Bundles

    Back to Main Menu
```

## Source Management Submenu

### Add New Source from RSS Feed

Quick way to add a new source:

**Steps:**
1. Select "Add New Source from RSS Feed"
2. Paste RSS feed URL
3. System auto-detects feed title
4. Enter source ID (suggested automatically)
5. Select category
6. Optionally add to bundle
7. Optionally test the source

**Example:**
```
Enter RSS feed URL: https://techcrunch.com/feed/

[OK] Feed 'TechCrunch' found.
Source ID: techcrunch
Category: tech
Add to bundle? Yes
  Bundle: tech
Test fetch? Yes
[OK] Source added and verified!
```

### List All Sources

Browse all available sources by category:

**Shows:**
- Source ID
- Display name
- Organized by category

**Select any source** to view details:
- ID, name, category
- Base URL
- Discovery method
- Source type (config-driven or custom)

### Test a Source

Verify a source works:

**Steps:**
1. Select "Test a Source"
2. Choose source from list
3. System fetches 3 sample articles
4. View results

**Use when:**
- Adding new source
- Troubleshooting
- Checking if source still works

### Remove Existing Sources

Clean up unused sources:

**Steps:**
1. Select "Remove Existing Sources"
2. Use Space to check sources to remove
3. Confirm removal
4. Automatic backup created
5. Sources removed

**Safety:**
- Backup created automatically
- Can undo if needed
- Usage statistics shown

## Pro Tips

**Fast Navigation:**
- Type first letter to jump to items starting with that letter
- Ctrl+C goes back without making changes
- Tab key for autocomplete (in text inputs)

**Efficient Workflow:**
- Use bundles for daily routine (fewer clicks)
- Use multi-source for custom combinations
- Use single URL for one-off articles

**No Typing Needed:**
- Everything is selectable with arrow keys
- No command memorization required
- Perfect for daily use

## Common Workflows

### Morning News Routine

```
1. ./capcat catch
2. Select: "Catch articles from a bundle of sources"
3. Choose: "tech"
4. HTML: "Yes"
5. Done - reading in browser
```

### Add and Test New Source

```
1. ./capcat catch
2. Select: "Manage Sources"
3. Select: "Add New Source from RSS Feed"
4. Paste URL
5. Follow prompts
6. Test: "Yes"
```

### Custom Selection

```
1. ./capcat catch
2. Select: "Catch articles from a list of sources"
3. Space to select: hn, bbc, nature
4. Enter to confirm
5. HTML: "Yes"
```

## When to Use Interactive Mode

**Use interactive mode when:**
- Starting your daily routine
- Adding/managing sources
- You want visual feedback
- You don't remember exact commands

**Use CLI instead when:**
- Automating with scripts
- Batch operations
- Faster for single repeated command
- Logging to file needed

## Next Steps

**Expand your workflow:**
- [Managing Sources](04-managing-sources.html) - Deep dive into source management
- [Bundles](05-bundles.html) - Create custom bundles

**Technical details:**
- [Interactive Mode Exhaustive](../02-interactive-mode-exhaustive.html) - Every function documented

## Quick Reference

```bash
# Start interactive mode
./capcat catch

# Navigation
Arrow keys   - Move selection
Enter        - Confirm
Space        - Toggle checkbox
Ctrl+C       - Go back
Tab          - Autocomplete

# Main menu shortcuts
1. Bundle selection
2. Multi-source selection
3. Single source
4. Single URL
5. Manage sources
6. Exit
```
