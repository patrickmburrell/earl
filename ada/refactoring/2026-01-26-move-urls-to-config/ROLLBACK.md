# Rollback Plan: Move Urls To Config

> **Project Type**: python-cli
> **For AI - Document Purpose**: Document how to undo refactoring if issues arise
> **Read this AFTER**: DESIGN.md (understand the changes first)
> **Use when**: Refactoring causes problems and needs to be reverted

**Date**: 2026-01-26

---

## If Issues Arise

```bash
# Revert code changes
cd /Users/AIUW003/Projects/PMB/earl
git revert <commit-hash>
git push github main

# Reinstall old version
uv tool uninstall earl  
uv tool install git+https://github.com/patrickmburrell/earl@<previous-commit>
```

---

## Data Safety

**No data loss risk**: Migration copies (doesn't move) urls.toml from dotfiles to `~/.config/earl/`. Original file in dotfiles is never deleted.

---

## Verification

- [ ] Earl reads from dotfiles location again
- [ ] `$EARL_DIR` override works
- [ ] Existing workflows restored
