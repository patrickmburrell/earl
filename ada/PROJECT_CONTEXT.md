# Project Context: earl

> **For AI**: Read this for Python CLI project overview, architecture, key decisions, and current state. Then check HISTORY.md for timeline.
> **Project Type**: python-cli
> **Last Updated**: 2026-01-26

---

## Current State
**Status**: [In Development / Production / Maintenance]
**Version**: [Current version]
**Installation**: uv tool install
**Code Size**: [Total lines, e.g., "~1200 lines"]
**Last Major Change**: [Brief description]

---

## 📋 Project Overview

### What We Built
[2-3 paragraphs describing the CLI tool - what it does, what commands it provides, why it exists]

### Problem It Solves
**Original Problem**: [The problem that motivated building this CLI]

**Solution**: [How this CLI solves it]

**Key Benefits**:
- Benefit 1 (e.g., automation, consistency, workflow improvement)
- Benefit 2
- Benefit 3

---

## 🛠️ Environment Details

### Platform & Tools
**Language**: Python 3.12+
**CLI Framework**: [typer / click / argparse]
**Package Manager**: uv
**Type Checking**: mypy
**Linting**: ruff
**Testing**: pytest
**Logging**: loguru
**IDE**: VSCode

### Project Structure
```
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── __main__.py      # Entry point
│       ├── cli.py           # CLI definition
│       ├── commands/        # Command modules
│       ├── config.py        # Configuration
│       └── utils.py         # Utilities
├── tests/
│   ├── test_cli.py
│   └── test_commands.py
├── ada/
├── pyproject.toml
├── README.md
└── .gitignore
```

### Key Configuration Files
**pyproject.toml**: Dependencies, entry points, build config, ruff settings
**src/project_name/__init__.py**: Version string
**src/project_name/config.py**: Runtime configuration (env vars, Path-based config)

---

## 🎯 Key Technical Decisions

### Decision 1: CLI Framework Choice
**Chosen**: [Framework name]

**Why**:
- [Specific reason for this project]
- [Another reason]

**Alternatives Considered**:
- ❌ **argparse**: Too verbose, manual help text
- ✅ **typer**: Rich integration, type-safe, automatic validation
- ❌ **click**: [Why not chosen]

**Implementation**: [Key details]

### Decision 2: Command Organization
**Approach**: [Single file / Command groups / Subcommands]

**Why**: [Scales well / Keeps code organized / etc.]

### Decision 3: [Another Key Decision]
**Chosen**: [What was decided]

**Why**: [Brief explanation]

---

## 🏗️ CLI Architecture

### Commands
**`command-name`**:
- Purpose: [What it does]
- Arguments: [arg1, arg2]
- Options: [--option1, --option2]
- Example: `cli-name command-name --option value`

**`another-command`**:
- Purpose: [What it does]
- Example: `cli-name another-command arg`

### Configuration
**Environment Variables**:
- `PROJECT_CONFIG_VAR`: [What it controls]

**Config File** (if applicable):
- Location: Uses pathlib.Path for all file operations
- Format: [TOML / JSON / YAML]

### Data Flow
```
User Input → CLI Parser → Command Handler → Business Logic → Output
```

---

## 📖 Usage

### Installation
```bash
# Development (editable install)
uv pip install --editable .

# Global installation
uv tool install --editable /path/to/project

# From PyPI (if published)
uv tool install project-name
```

### Running
```bash
# Show help
project-name --help

# Common command
project-name command-name --option value

# Development (without install)
python -m project_name command-name
```

### Common Operations
```bash
# Operation 1
project-name operation1 args

# Operation 2
project-name operation2 --flag
```

---

## 🧪 Testing

### Test Strategy
- **Unit tests**: CLI command logic, utilities
- **Integration tests**: Full command execution with CliRunner
- **Manual testing**: Interactive UX, help text, error messages

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_cli.py

# With coverage
pytest --cov=src/project_name --cov-report=html

# Type checking
mypy src/

# Linting
ruff check src/
```

### Testing CLI Commands
```python
from typer.testing import CliRunner
from project_name.cli import app

runner = CliRunner()
result = runner.invoke(app, ["command", "arg"])
assert result.exit_code == 0
```

---

## 🚀 Distribution

### Building
```bash
# Build distribution packages
python -m build

# Verify package
twine check dist/*
```

### Installation Methods
- **uv tool**: Primary distribution method
- **PyPI**: For public tools
- **Homebrew**: For wider macOS distribution (if needed)

---

## ⚠️ Common Issues

### Issue 1: Command Not Found After Install
**Symptom**: `command not found: project-name`

**Cause**: Entry point not registered or uv tool path not in PATH

**Solution**:
```bash
# Verify entry point in pyproject.toml
[project.scripts]
project-name = "project_name.cli:main"

# Reinstall with uv
uv tool install --editable /path/to/project --force
```

### Issue 2: Import Errors in Development
**Symptom**: `ModuleNotFoundError: No module named 'project_name'`

**Cause**: Not installed in editable mode

**Solution**:
```bash
uv pip install --editable .
```

---

## 📁 Files Inventory

| File                          | Purpose                                     |
|-------------------------------|---------------------------------------------|
| `src/project_name/cli.py`     | CLI definition, command registration        |
| `src/project_name/__main__.py`| Entry point for `python -m project_name`    |
| `src/project_name/commands/`  | Command implementations                     |
| `src/project_name/config.py`  | Configuration management                    |
| `pyproject.toml`              | Dependencies, scripts, build config, ruff   |

---

## 📝 Notes

### Future Enhancements
- [ ] [Feature name]: What it will add, why users need it
- [ ] [Another feature]: Improvement to existing functionality

### Technical Debt
- [Debt item]: Why it exists, when to address

---

**For timeline and evolution, see HISTORY.md**
