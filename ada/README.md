# Ada Context Guide

> **For AI Assistants**: This directory contains structured context to help you work effectively on this project. Follow the workflow below based on what you're doing.

---

## 🚀 Quick Start

**Every session should start here:**
1. **Read `PROJECT_CONTEXT.md`** - Understand what this project is, its current state, and key decisions
2. **Read `HISTORY.md`** - See the timeline of major changes
3. **Then follow the appropriate workflow below**

---

## 📋 Workflows

### New Project
**Directory**: `new-project/`
**Use when**: Starting a brand new project from scratch

**Sequence**:
1. `REQUIREMENTS.md` - Define WHAT to build (problem, solution, success criteria)
2. `DESIGN.md` - Decide HOW to build it (architecture, decisions, patterns)
3. `PLAN.md` - Track implementation progress (checkboxes, phases)
4. `PROJECT_CONTEXT.md` - Write the project overview (update as you go)
5. `HISTORY.md` - Start the timeline

**After completion**: Move these to the root `ada/` directory

---

### Feature Addition
**Directory**: `features/[feature-name]/`
**Use when**: Adding new functionality to existing project

**Sequence**:
1. `REQUIREMENTS.md` - Define WHAT feature to add (gap, requirements, scope)
2. `DESIGN.md` - Decide HOW to implement (integration points, changes needed)
3. `PLAN.md` - Track implementation (steps, testing, completion)

**After completion**: 
- Update root `PROJECT_CONTEXT.md` with new feature
- Add entry to `HISTORY.md`
- Archive feature docs or keep for reference

---

### Bug Investigation
**Directory**: `investigations/[issue-description]/`
**Use when**: Debugging issues, investigating problems

**Sequence**:
1. `INVESTIGATION.md` - Document the problem (symptoms, reproduction, root cause)
2. `RESOLUTION.md` - Document the fix (solution, implementation, testing)
3. `FINDINGS.md` - Document results (verification, lessons learned, prevention)

**After completion**: 
- Add entry to `HISTORY.md`
- Update `PROJECT_CONTEXT.md` if this revealed architectural issues

---

### Refactoring
**Directory**: `refactoring/[refactoring-name]/`
**Use when**: Improving code structure without changing behavior

**Sequence**:
1. `ANALYSIS.md` - Why refactor (problems, goals, constraints)
2. `DESIGN.md` - How to refactor (approach, before/after, migration)
3. `PLAN.md` - Track refactoring (preparation, changes, validation)
4. `ROLLBACK.md` - Document how to undo if needed

**After completion**:
- Update `PROJECT_CONTEXT.md` with new patterns
- Add entry to `HISTORY.md`

---

### Experiment
**Directory**: `experiments/[experiment-name]/`
**Use when**: Testing hypotheses, evaluating approaches, A/B testing

**Sequence**:
1. `HYPOTHESIS.md` - What are we testing (question, hypothesis, design)
2. `RESULTS.md` - What happened (data, analysis, validation)
3. `DECISION.md` - What to do (adopt/abandon/iterate, next steps)

**After completion**:
- If adopted: Update `PROJECT_CONTEXT.md` and `HISTORY.md`
- If abandoned: Document why for future reference

---

## 📄 Document Purposes

| Document             | Purpose                                   | Update Frequency                   |
|----------------------|-------------------------------------------|------------------------------------|
| `PROJECT_CONTEXT.md` | Living overview of the project            | Update after major changes         |
| `HISTORY.md`         | Timeline of project evolution             | Add entry after each workflow      |
| `REQUIREMENTS.md`    | Define WHAT (problem, solution, scope)    | Created once per workflow          |
| `DESIGN.md`          | Define HOW (architecture, approach)       | Created once per workflow          |
| `PLAN.md`            | Track implementation progress             | Update as work progresses          |

---

## 🎯 Best Practices for AI Assistants

1. **Always start with PROJECT_CONTEXT.md** - Don't skip this step
2. **Follow the sequence** - Requirements → Design → Plan (don't jump ahead)
3. **Update living documents** - PROJECT_CONTEXT and HISTORY get updated after each workflow
4. **Keep workflow docs in subdirectories** - Don't clutter the root ada/ directory
5. **Archive completed workflows** - Move to `archive/` if they're no longer relevant

---

## 🗂️ Directory Structure

```
ada/
├── README.md                    # This file
├── PROJECT_CONTEXT.md           # Living project overview
├── HISTORY.md                   # Project timeline
├── new-project/                 # Templates for new projects
├── features/                    # Feature additions
│   └── [feature-name]/
│       ├── REQUIREMENTS.md
│       ├── DESIGN.md
│       └── PLAN.md
├── investigations/              # Bug investigations
│   └── [issue-description]/
│       ├── INVESTIGATION.md
│       ├── RESOLUTION.md
│       └── FINDINGS.md
├── refactoring/                 # Code refactoring
│   └── [refactoring-name]/
│       ├── ANALYSIS.md
│       ├── DESIGN.md
│       ├── PLAN.md
│       └── ROLLBACK.md
├── experiments/                 # Hypothesis testing
│   └── [experiment-name]/
│       ├── HYPOTHESIS.md
│       ├── RESULTS.md
│       └── DECISION.md
└── archive/                     # Completed workflows (optional)
```

---

## 💡 Quick Reference

**"I'm starting a new project"** → `new-project/`
**"I need to add a feature"** → `features/[name]/`
**"Something's broken"** → `investigations/[issue]/`
**"This code is messy"** → `refactoring/[name]/`
**"I want to try something"** → `experiments/[name]/`

**Always remember**: Read PROJECT_CONTEXT.md first!
