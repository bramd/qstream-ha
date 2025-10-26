# QStream Claude Code Skills

Project-specific skills for working with the QStream Home Assistant integration.

**Installation:** See [../../.claude/README.md](../../.claude/README.md) for setup instructions.

## Available Skills

### `/qstream:cutting-a-release`

**Location:** `.claude/commands/qstream/cutting-a-release.md` (in this repo)

**Purpose:** Automate QStream integration releases with safety checks and atomic workflow.

**When to use:** Ready to release a new QStream version

**What it does:**
- Runs pre-release checks (CI status, clean working directory, on main branch)
- Calculates suggested version from conventional commits (with override option)
- Auto-generates release notes from commit history
- Updates manifest.json and CHANGELOG.md
- Shows preview before publishing
- Creates git tag and GitHub Release atomically

**Key features:**
- Atomic workflow: prepare → preview → publish
- All changes prepared first, single review point
- No partial states - all-or-nothing execution
- Semantic versioning with auto-suggestion
- Error recovery guidance for network failures

**Usage:**
```
/qstream:cutting-a-release
```

The skill guides you through the entire process interactively.

## Skill Development

These skills were developed using Test-Driven Development for documentation:
1. **RED:** Test baseline behavior without skill, document failures
2. **GREEN:** Write minimal skill addressing failures
3. **REFACTOR:** Close loopholes found in testing

All skills tested with subagents under pressure scenarios (time pressure, skip steps, dirty state) to ensure they resist rationalization and enforce best practices.

## Design Documents

Corresponding design documents in `docs/plans/`:
- `2025-10-26-release-skill-design.md` - Complete design specification for cutting-a-release skill
