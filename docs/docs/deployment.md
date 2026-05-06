---
layout: default
render_with_liquid: false
---

# Deployment

Capcat is a CLI tool installed per-user. There is no server to deploy.

## Install for a User

```bash
pipx install capcat
```

`pipx` installs Capcat in an isolated virtualenv and adds `capcat` to `~/.local/bin`. Recommended for end users.

## Install for Development

```bash
git clone https://github.com/stayukasabov/capcat.git
cd capcat
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

`pip install -e .` installs in editable mode — source changes take effect immediately without reinstalling.

## Update

```bash
# pipx install
pipx upgrade capcat

# editable install — pull and the changes are live
cd ~/capcat && git pull
```

## Scheduled Fetching

Capcat has no built-in scheduler. Use cron:

```cron
# Fetch tech bundle daily at 07:00
0 7 * * * /home/user/.local/bin/capcat bundle tech --count 30 --html
```

## Output Location

By default, output is written to the current working directory. Pin a location with `--output`:

```bash
capcat fetch hn --count 30 --html --output ~/News
```

Or set a consistent working directory in your cron job / shell alias.

## PyPI

Published to PyPI at each tagged release. Version follows semantic versioning (patch / minor / major).

```bash
pip show capcat   # check installed version
```
