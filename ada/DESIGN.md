# Design: earl

> **Project Type**: python-cli
> **For AI - Document Purpose**: Define HOW to build (architecture, decisions, approach, patterns)
> **Read this AFTER**: REQUIREMENTS.md (know what you're building first)
> **Next step**: PLAN.md (track implementation progress)

**Date**: 2026-01-26
**Status**: Draft

---

## Overview

**Purpose**: [One sentence: This CLI tool provides...]
**Approach**: [High-level approach: Command-based interface using typer/click with...]

---

## Architecture

### Component Structure
```
src/project_name/
├── cli.py           # Main CLI app, command registration
├── __main__.py      # Entry point
├── commands/
│   ├── command1.py  # Command implementations
│   └── command2.py
├── config.py        # Configuration management
├── models.py        # Data models (if needed)
└── utils.py         # Shared utilities
```

### Command Flow
```
CLI Entry Point (cli.py)
    ↓
Command Parser ([framework])
    ↓
Command Handler (commands/*.py)
    ↓
Business Logic
    ↓
Output (Rich console)
```

---

## Key Design Decisions

### Decision 1: CLI Framework
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| typer | Type-safe, Rich integration, auto help | Opinionated | ✅ SELECTED - Best for Python 3.14+, Rich output |
| click | Mature, flexible | Manual type handling | ❌ Rejected - Typer is better for new projects |
| argparse | Built-in, no deps | Verbose, manual everything | ❌ Rejected - Too low-level |

**Rationale**: [Specific reason for this project]

---

### Decision 2: Configuration Strategy
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Env vars only | Simple, 12-factor | Limited for complex config | [Selected/Rejected] |
| Config file only | Rich config, shareable | Extra file to manage | [Selected/Rejected] |
| Hybrid (both) | Flexible, overrideable | More complex | ✅ SELECTED |

**Implementation**:
- Config file: `~/.config/project-name/config.toml`
- Env vars: `PROJECT_*` prefix
- CLI args override all
- Uses pathlib.Path for file operations

---

### Decision 3: Error Handling Strategy
**Approach**: [How errors are handled]

**Details**:
- User errors: Rich formatted messages, no stack trace
- System errors: Log with loguru, show user-friendly message
- Exit codes: 0=success, 1=user error, 2=system error

---

## Data Models

### [Model Name] (if applicable)
```python
@dataclass
class ModelName:
    field1: str
    field2: int | None
```

---

## External Dependencies

### Core Dependencies
- **typer**: CLI framework
- **rich**: Terminal formatting, progress bars
- **loguru**: Logging
- **[other]**: Purpose

### Dev Dependencies
- **pytest**: Testing
- **ruff**: Linting
- **ty/mypy**: Type checking

---

## Commands Specification

### Command: `command-name`
**Purpose**: [What it does]

**Syntax**:
```bash
cli-name command-name ARG [OPTIONS]
```

**Arguments**:
- `ARG`: [Description, type]

**Options**:
- `--option1 VALUE`: [Description, default]
- `--flag`: [Description]

**Output**: [What user sees]

**Error Handling**: [Common errors and messages]

---

### Command: `another-command`
[Repeat structure]

---

## Configuration Schema

```toml
[section]
key = "value"
another_key = 123

[another_section]
setting = true
```

---

## Testing Strategy

### Unit Tests
- Test each command handler independently
- Mock external dependencies
- Test error conditions

### Integration Tests
- Use `CliRunner` to test full command execution
- Test with real (test) configuration
- Verify output format

### Manual Tests
- Help text clarity
- Error message helpfulness
- UX flow

---

## Deployment

### Distribution
- **Primary**: `uv tool install`
- **Alternative**: PyPI (if public)

### Installation
```bash
# Development
uv pip install --editable .

# Global
uv tool install --editable /path/to/project
```

---

## Future Considerations

### Potential Enhancements
- [Feature idea]: Why it might be valuable
- [Another idea]: When it would make sense

### Known Limitations
- [Limitation]: Why it exists, when to address

---

**Next**: See PLAN.md for implementation steps
