# Claude Code Configuration for QStream

This directory contains Claude Code skills and configuration for the QStream Home Assistant integration project.

## Setup for Contributors

To use the QStream-specific skills in this repository:

### Option 1: Symlink (Recommended - Auto-updates)

Create a symlink from your personal Claude commands directory to this repo's commands:

**Windows (PowerShell as Administrator):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\qstream" -Target "C:\path\to\qstream-ha\.claude\commands\qstream"
```

**macOS/Linux:**
```bash
ln -s /path/to/qstream-ha/.claude/commands/qstream ~/.claude/commands/qstream
```

**Benefits:**
- Skills automatically update when you pull repo changes
- One source of truth
- Changes you make are immediately in the repo

### Option 2: Copy (Simple - Manual updates)

Copy the skills to your personal Claude commands directory:

**All platforms:**
```bash
cp -r .claude/commands/qstream ~/.claude/commands/qstream
```

**Benefits:**
- Simple one-time setup
- No symlink requirements

**Drawback:** Need to manually re-copy when skills are updated in the repo

## Verification

After setup, verify the skill is available:

```bash
# Check if skill file exists in your personal commands
ls ~/.claude/commands/qstream/cutting-a-release.md

# Or on Windows
dir %USERPROFILE%\.claude\commands\qstream\cutting-a-release.md
```

You should now be able to use:
```
/qstream:cutting-a-release
```

## Available Skills

See [docs/skills/README.md](../docs/skills/README.md) for detailed documentation of available skills, including:
- What each skill does
- When to use it
- Key features and usage examples

## Contributing Skills

When creating new QStream-specific skills:

1. Create the skill file in `.claude/commands/qstream/`
2. Test it using the TDD methodology (see existing skills)
3. Document it in `docs/skills/README.md`
4. Create a design document in `docs/plans/` if complex
5. Commit both the skill and documentation to the repo

This ensures all contributors have access to the same workflows.
