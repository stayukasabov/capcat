# GitHub CLI (gh) Tutorial

## What is GitHub CLI?

GitHub CLI (`gh`) is the official command-line tool for interacting with GitHub. It allows you to manage pull requests, issues, repositories, and more without leaving the terminal.

## Installation

### macOS
```bash
brew install gh
```

### Linux
```bash
# Debian/Ubuntu
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Fedora/CentOS
sudo dnf install gh
```

### Windows
```bash
winget install --id GitHub.cli
# or
scoop install gh
```

## Authentication

### First-time Setup

```bash
gh auth login
```

Follow the prompts:
1. Choose GitHub.com or GitHub Enterprise Server
2. Choose HTTPS or SSH
3. Authenticate via web browser or paste token
4. Verify: `gh auth status`

### Check Authentication

```bash
gh auth status
```

### Switch Accounts

```bash
gh auth switch
```

### Logout

```bash
gh auth logout
```

## Pull Requests

### Create Pull Request

From current branch:
```bash
gh pr create
```

With title and body:
```bash
gh pr create --title "Fix hanging issue" --body "This PR fixes the threading deadlock"
```

Multi-line body:
```bash
gh pr create --title "Fix hanging issue" --body "$(cat <<'EOF'
## Summary
- Fixed nested ThreadPoolExecutor deadlock
- Added shared conversion executor

## Test Plan
- Tested batch fetch with 3 articles
- Verified no hangs occur
EOF
)"
```

To specific branch:
```bash
gh pr create --base main --head feature-branch
```

Draft PR:
```bash
gh pr create --draft
```

### List Pull Requests

All open PRs:
```bash
gh pr list
```

Your PRs:
```bash
gh pr list --author @me
```

By state:
```bash
gh pr list --state open
gh pr list --state closed
gh pr list --state merged
```

Limit results:
```bash
gh pr list --limit 10
```

### View Pull Request

View in terminal:
```bash
gh pr view 123
```

View in browser:
```bash
gh pr view 123 --web
```

View current branch's PR:
```bash
gh pr view
```

Show diff:
```bash
gh pr diff 123
```

### Checkout Pull Request

```bash
gh pr checkout 123
```

By branch name:
```bash
gh pr checkout feature-branch
```

### Review Pull Request

Start review:
```bash
gh pr review 123
```

Approve:
```bash
gh pr review 123 --approve
```

Request changes:
```bash
gh pr review 123 --request-changes --body "Please add tests"
```

Comment:
```bash
gh pr review 123 --comment --body "Looks good overall"
```

### Merge Pull Request

Merge:
```bash
gh pr merge 123
```

Merge with strategy:
```bash
gh pr merge 123 --merge      # Create merge commit
gh pr merge 123 --squash     # Squash and merge
gh pr merge 123 --rebase     # Rebase and merge
```

Auto-merge when checks pass:
```bash
gh pr merge 123 --auto --squash
```

Delete branch after merge:
```bash
gh pr merge 123 --delete-branch
```

### Close Pull Request

```bash
gh pr close 123
```

With comment:
```bash
gh pr close 123 --comment "No longer needed"
```

### Reopen Pull Request

```bash
gh pr reopen 123
```

### Pull Request Checks

View status checks:
```bash
gh pr checks 123
```

Watch checks in real-time:
```bash
gh pr checks 123 --watch
```

## Issues

### Create Issue

```bash
gh issue create
```

With title and body:
```bash
gh issue create --title "Fix timeout handling" --body "Need to improve timeout logic"
```

With labels:
```bash
gh issue create --title "Bug: hanging" --label bug,high-priority
```

Assign to someone:
```bash
gh issue create --title "Feature request" --assignee username
```

### List Issues

All open issues:
```bash
gh issue list
```

Your issues:
```bash
gh issue list --assignee @me
```

By label:
```bash
gh issue list --label bug
gh issue list --label "high-priority"
```

By state:
```bash
gh issue list --state open
gh issue list --state closed
gh issue list --state all
```

### View Issue

```bash
gh issue view 42
```

View in browser:
```bash
gh issue view 42 --web
```

Show comments:
```bash
gh issue view 42 --comments
```

### Close Issue

```bash
gh issue close 42
```

With comment:
```bash
gh issue close 42 --comment "Fixed in PR #123"
```

### Reopen Issue

```bash
gh issue reopen 42
```

### Comment on Issue

```bash
gh issue comment 42 --body "Working on this now"
```

Edit comment:
```bash
gh issue comment 42 --edit
```

## Repository Management

### View Repository

Current repo info:
```bash
gh repo view
```

Specific repo:
```bash
gh repo view owner/repo
```

View in browser:
```bash
gh repo view --web
```

### Clone Repository

```bash
gh repo clone owner/repo
```

Clone to specific directory:
```bash
gh repo clone owner/repo target-dir
```

### Fork Repository

Fork current repo:
```bash
gh repo fork
```

Fork specific repo:
```bash
gh repo fork owner/repo
```

Fork and clone:
```bash
gh repo fork owner/repo --clone
```

### Create Repository

```bash
gh repo create my-new-repo
```

With description:
```bash
gh repo create my-new-repo --description "My awesome project"
```

Private repo:
```bash
gh repo create my-new-repo --private
```

Public repo:
```bash
gh repo create my-new-repo --public
```

With README:
```bash
gh repo create my-new-repo --public --add-readme
```

From current directory:
```bash
gh repo create --source=. --private --push
```

### Delete Repository

```bash
gh repo delete owner/repo
```

Confirm deletion:
```bash
gh repo delete owner/repo --yes
```

### Repository Settings

Enable issues:
```bash
gh repo edit --enable-issues
```

Disable wiki:
```bash
gh repo edit --disable-wiki
```

Set description:
```bash
gh repo edit --description "News archiving system"
```

Set homepage:
```bash
gh repo edit --homepage "https://example.com"
```

## Releases

### List Releases

```bash
gh release list
```

Limit results:
```bash
gh release list --limit 5
```

### View Release

Latest release:
```bash
gh release view
```

Specific release:
```bash
gh release view v2.0.0
```

View in browser:
```bash
gh release view v2.0.0 --web
```

### Create Release

```bash
gh release create v2.0.0
```

With title and notes:
```bash
gh release create v2.0.0 --title "Version 2.0.0" --notes "Major update with bug fixes"
```

From notes file:
```bash
gh release create v2.0.0 --notes-file RELEASE_NOTES.md
```

With assets:
```bash
gh release create v2.0.0 dist/*.tar.gz dist/*.zip
```

Draft release:
```bash
gh release create v2.0.0 --draft
```

Pre-release:
```bash
gh release create v2.0.0-beta --prerelease
```

### Download Release Assets

Latest release:
```bash
gh release download
```

Specific release:
```bash
gh release download v2.0.0
```

Specific asset pattern:
```bash
gh release download v2.0.0 --pattern '*.tar.gz'
```

### Delete Release

```bash
gh release delete v2.0.0
```

With confirmation:
```bash
gh release delete v2.0.0 --yes
```

## Workflows (GitHub Actions)

### List Workflows

```bash
gh workflow list
```

### View Workflow

```bash
gh workflow view "CI"
```

View in browser:
```bash
gh workflow view "CI" --web
```

### Run Workflow

```bash
gh workflow run "CI"
```

On specific branch:
```bash
gh workflow run "CI" --ref feature-branch
```

With inputs:
```bash
gh workflow run "Deploy" -f environment=production
```

### View Workflow Runs

```bash
gh run list
```

For specific workflow:
```bash
gh run list --workflow="CI"
```

Recent runs:
```bash
gh run list --limit 10
```

### View Run Details

```bash
gh run view 123456
```

View in browser:
```bash
gh run view 123456 --web
```

Show logs:
```bash
gh run view 123456 --log
```

### Download Run Artifacts

```bash
gh run download 123456
```

Specific artifact:
```bash
gh run download 123456 --name test-results
```

### Rerun Workflow

```bash
gh run rerun 123456
```

Rerun failed jobs only:
```bash
gh run rerun 123456 --failed
```

### Cancel Run

```bash
gh run cancel 123456
```

### Watch Run

Monitor run in real-time:
```bash
gh run watch 123456
```

## Gists

### Create Gist

From file:
```bash
gh gist create script.py
```

Multiple files:
```bash
gh gist create file1.py file2.py
```

Public gist:
```bash
gh gist create --public script.py
```

From stdin:
```bash
echo "Hello, World!" | gh gist create --filename hello.txt
```

With description:
```bash
gh gist create script.py --desc "Useful script"
```

### List Gists

Your gists:
```bash
gh gist list
```

Public gists:
```bash
gh gist list --public
```

Limit results:
```bash
gh gist list --limit 10
```

### View Gist

```bash
gh gist view abc123
```

View in browser:
```bash
gh gist view abc123 --web
```

View specific file:
```bash
gh gist view abc123 --filename script.py
```

### Edit Gist

```bash
gh gist edit abc123
```

Add file:
```bash
gh gist edit abc123 --add newfile.py
```

### Delete Gist

```bash
gh gist delete abc123
```

## Advanced Features

### API Calls

Make raw API calls:
```bash
gh api repos/owner/repo
```

With pagination:
```bash
gh api --paginate repos/owner/repo/issues
```

POST request:
```bash
gh api repos/owner/repo/issues -f title="Bug report" -f body="Description"
```

### Aliases

Create alias:
```bash
gh alias set pv 'pr view'
```

Use alias:
```bash
gh pv 123
```

List aliases:
```bash
gh alias list
```

Delete alias:
```bash
gh alias delete pv
```

### Extensions

List extensions:
```bash
gh extension list
```

Install extension:
```bash
gh extension install owner/gh-extension-name
```

Update extensions:
```bash
gh extension upgrade --all
```

Remove extension:
```bash
gh extension remove extension-name
```

## Common Workflows

### Complete PR Workflow

```bash
# 1. Create feature branch
git checkout -b fix-hanging-issue

# 2. Make changes and commit
git add core/
git commit -m "Fix hanging issue"

# 3. Push branch
git push -u origin fix-hanging-issue

# 4. Create PR
gh pr create --title "Fix hanging issue" --body "$(cat <<'EOF'
## Summary
- Fixed nested ThreadPoolExecutor deadlock

## Changes
- Created shared conversion executor
- Updated article_fetcher.py

## Test Plan
- Tested batch fetch with 3 articles
- Verified no hangs occur
EOF
)"

# 5. Check CI status
gh pr checks --watch

# 6. Merge when ready
gh pr merge --squash --delete-branch
```

### Issue to PR Workflow

```bash
# 1. Create issue
gh issue create --title "Fix timeout handling" --label bug

# 2. Create branch from issue
git checkout -b fix-timeout-42

# 3. Make changes and push
git add .
git commit -m "Fix timeout handling (closes #42)"
git push -u origin fix-timeout-42

# 4. Create PR that references issue
gh pr create --title "Fix timeout handling" --body "Closes #42"

# 5. Merge PR (automatically closes issue)
gh pr merge --squash
```

### Release Workflow

```bash
# 1. Create and push tag
git tag -a v2.0.0 -m "Version 2.0.0"
git push origin v2.0.0

# 2. Create release with assets
gh release create v2.0.0 \
  --title "Version 2.0.0" \
  --notes-file RELEASE_NOTES.md \
  dist/*.tar.gz dist/*.zip

# 3. View release
gh release view v2.0.0 --web
```

### Collaboration Workflow

```bash
# 1. Fork repo
gh repo fork owner/repo --clone

# 2. Create feature branch
cd repo
git checkout -b my-feature

# 3. Make changes and commit
git add .
git commit -m "Add new feature"

# 4. Push to your fork
git push -u origin my-feature

# 5. Create PR to upstream
gh pr create --repo owner/repo \
  --title "Add new feature" \
  --body "This PR adds..."

# 6. Respond to review
gh pr review 123 --comment --body "Updated per feedback"
```

## Configuration

### Config Files

Location: `~/.config/gh/config.yml`

View config:
```bash
gh config list
```

Set values:
```bash
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt enabled
```

### Default Repository

Set default repo for commands:
```bash
gh repo set-default
```

Use in commands:
```bash
# These will use default repo
gh issue list
gh pr list
```

### Output Formatting

JSON output:
```bash
gh pr list --json number,title,state
```

Custom template:
```bash
gh pr list --template '{{range .}}{{.number}}: {{.title}}{{"\n"}}{{end}}'
```

## Troubleshooting

### Authentication Issues

Re-authenticate:
```bash
gh auth login --force
```

Use token:
```bash
gh auth login --with-token < token.txt
```

### Rate Limiting

Check rate limit:
```bash
gh api rate_limit
```

### Debug Mode

Enable verbose output:
```bash
GH_DEBUG=api gh pr list
```

## Quick Reference

```bash
# Pull Requests
gh pr create                  # Create PR
gh pr list                    # List PRs
gh pr view 123                # View PR
gh pr checkout 123            # Checkout PR
gh pr merge 123               # Merge PR
gh pr close 123               # Close PR

# Issues
gh issue create               # Create issue
gh issue list                 # List issues
gh issue view 42              # View issue
gh issue close 42             # Close issue
gh issue reopen 42            # Reopen issue

# Repository
gh repo view                  # View repo
gh repo clone owner/repo      # Clone repo
gh repo fork                  # Fork repo
gh repo create my-repo        # Create repo

# Releases
gh release list               # List releases
gh release create v1.0.0      # Create release
gh release download           # Download release

# Workflows
gh workflow list              # List workflows
gh workflow run "CI"          # Run workflow
gh run list                   # List runs
gh run view 123456            # View run

# Gists
gh gist create file.py        # Create gist
gh gist list                  # List gists
gh gist view abc123           # View gist

# Authentication
gh auth login                 # Login
gh auth status                # Check status
gh auth logout                # Logout
```

## Tips and Best Practices

1. **Use Interactive Mode**
   - Many commands (like `gh pr create`) have interactive prompts
   - Just run the base command and answer questions

2. **Combine with Git**
   - `gh` works alongside regular git commands
   - Use git for local operations, gh for GitHub interactions

3. **Use JSON Output for Scripting**
   ```bash
   gh pr list --json number,title --jq '.[] | select(.title | contains("bug"))'
   ```

4. **Save Time with Aliases**
   ```bash
   gh alias set bugs 'issue list --label bug'
   gh bugs
   ```

5. **Web Fallback**
   - Most commands support `--web` to open in browser
   - Useful for complex operations

6. **Tab Completion**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   eval "$(gh completion -s bash)"  # bash
   eval "$(gh completion -s zsh)"   # zsh
   ```

## Resources

- Official docs: https://cli.github.com/manual/
- GitHub repo: https://github.com/cli/cli
- Community: https://github.com/cli/cli/discussions

## Help

Get help for any command:
```bash
gh help
gh pr --help
gh issue create --help
```
