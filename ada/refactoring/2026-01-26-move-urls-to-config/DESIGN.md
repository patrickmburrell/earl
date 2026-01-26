# Refactoring Design: Move Urls To Config

> **Project Type**: python-cli
> **For AI - Document Purpose**: Define HOW to build (architecture, decisions, approach, patterns)
> **Read this AFTER**: REQUIREMENTS.md (know what you're building first)
> **Next step**: PLAN.md (track implementation progress)

**Date**: 2026-01-26

---

## Approach

Update `config.py::get_urls_file()` to check locations in priority order:
1. `$EARL_DIR/urls.toml` (explicit override)
2. `~/.config/earl/urls.toml` (new default)
3. `$DOTFILES_ROOT/os/mac/bin/earl/urls.toml` (backwards compatibility)

If dotfiles location exists but `~/.config/earl/urls.toml` doesn't, automatically copy it (one-time migration).

---

## Changes

**`src/earl/config.py`**:
- Update `get_urls_file()` function with new priority logic
- Add `_migrate_from_dotfiles()` helper function
- Create `~/.config/earl/` directory if needed

**Documentation**:
- `README.md`: Update configuration section
- `PROJECT_CONTEXT.md`: Update key configuration files
- Add migration note for existing users

---

**Next**: See PLAN.md
