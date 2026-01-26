# Refactoring Plan: Move Urls To Config

> **Project Type**: python-cli
> **For AI - Document Purpose**: Track implementation progress (steps, checkboxes, phases)
> **Read this AFTER**: DESIGN.md (know how you're building first)
> **During implementation**: Update checkboxes as work completes

**Date**: 2026-01-26

---

## Steps

- [x] Update `src/earl/config.py::get_urls_file()` with new priority logic
- [x] Add `_migrate_from_dotfiles()` helper function
- [x] Test manually: `earl --help` with no config
- [x] Test manually: `earl --list-profiles`
- [x] Test manually: migration from dotfiles
- [x] Test manually: `$EARL_DIR` override still works
- [x] Update README.md configuration section
- [x] Update PROJECT_CONTEXT.md key configuration files
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] Reinstall: `uv tool install --force git+https://github.com/patrickmburrell/earl`
- [ ] Final test on installed version

---

**Rollback**: See ROLLBACK.md
