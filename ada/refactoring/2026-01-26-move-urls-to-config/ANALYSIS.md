# Refactoring Analysis: Move Urls To Config

> **Project Type**: python-cli
> **For AI - Document Purpose**: Document why refactor (problems, goals, constraints, risks)
> **Start here**: When planning code refactoring
> **Next step**: DESIGN.md (decide how to refactor)

**Date**: 2026-01-26

---

## Problem

**Current State**: Earl reads global URLs from `$DOTFILES_ROOT/os/mac/bin/earl/urls.toml`. This couples Earl to dotfiles structure and makes it dependent on `$DOTFILES_ROOT` being set.

**Why**: The urls.toml file is only used by Earl (not by shell or other tools), so it should live in Earl's own config directory. This makes Earl self-contained and follows XDG standards.

---

## Goals

- [ ] Move global urls.toml to `~/.config/earl/urls.toml`
- [ ] Keep `$EARL_DIR` override for flexibility  
- [ ] Auto-migrate from dotfiles on first run
- [ ] Update documentation
- [ ] Maintain backwards compatibility during transition

---

**Next**: See DESIGN.md
