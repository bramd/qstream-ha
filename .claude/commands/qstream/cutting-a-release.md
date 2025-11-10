---
name: qstream-cutting-a-release
description: Use when ready to release a new QStream version - automates version management, changelog updates, and GitHub release creation with safety checks and preview-before-publish workflow
---

# Cutting a QStream Release

## Overview

Automate QStream integration releases with atomic workflow: prepare changes → preview → publish.

**Core principle:** All changes prepared first, single review point, atomic execution.

**Announce at start:** "I'm using the qstream:cutting-a-release skill to create this release."

## Process

### Step 1: Pre-Release Checks

**All checks must pass before proceeding:**

```bash
# 1. Verify on main branch
git branch --show-current  # Must output: main

# 2. Working directory must be clean
git status --porcelain  # Must be empty

# 3. Verify CI passes
gh run list --branch main --limit 1 --json conclusion
# Must show: "conclusion": "success"

# 4. Sync with remote
git fetch origin main
git rev-list HEAD..origin/main --count  # Must be 0
```

**If any check fails, STOP:**
- Not on main → git checkout main
- Dirty working directory → Commit or stash changes first
- CI failing → Fix issues before releasing
- Behind origin → git pull origin main

**Never skip pre-checks to save time.** Dirty state mid-release wastes more time than upfront verification.

### Step 2: Version Calculation

**Find last release:**
```bash
git describe --tags --abbrev=0 --match "v*"
# Example output: v0.2.0
# If no tags exist: Start at v0.1.0
```

**Analyze commits since last release:**
```bash
LAST_TAG=$(git describe --tags --abbrev=0 --match "v*" 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
  # No previous tags - show all commits
  git log --oneline --pretty=format:"%s"
else
  # Show commits since last tag
  git log ${LAST_TAG}..HEAD --oneline --pretty=format:"%s"
fi
```

**Version bump logic (Semantic Versioning):**
- BREAKING CHANGE or exclamation mark in commit = **Major bump** (0.2.0 to 1.0.0)
- feat: or feat(...) = **Minor bump** (0.2.0 to 0.3.0)
- fix: = **Patch bump** (0.2.0 to 0.2.1)
- Other (docs, chore, ci) = **Patch bump** (default)

**Present suggestion to user:**
```
Suggested version: v0.3.0 (minor bump)
Reason: Found 1 feature, 2 fixes since v0.2.0

Commits analyzed:
- feat: add Dutch translation support
- fix: update HACS validation
- docs: add brand assets design

Accept v0.3.0 or specify different version?
```

**If user overrides:** Validate format (must be X.Y.Z) and check uniqueness:
```bash
git tag --list "v${USER_VERSION}"  # Must be empty
```

### Step 3: Generate Release Notes

**Parse commits by type:**
```bash
git log ${LAST_TAG}..HEAD --pretty=format:"%s|||%b"
```

**Categorize:**
- **Breaking Changes** - BREAKING CHANGE in body or exclamation mark after type
- **Features** - feat: or feat(...)
- **Bug Fixes** - fix: or fix(...)
- **Documentation** - docs:
- **Other** - Everything else (ci, chore, test, refactor)

**Generate markdown:**
```markdown
## What's Changed

### Features
- Add Dutch translation support (#3)

### Bug Fixes
- Update HACS validation configuration (#2)

### Documentation
- Add brand assets design document

**Full Changelog**: https://github.com/bramd/qstream-ha/compare/v0.2.0...v0.3.0
```

**Extract PR numbers:** Look for (#123) patterns in commit messages.

**Present to user:**
```
Generated release notes:
[Show full markdown]

Options:
1. Use as-is
2. Edit notes
3. Cancel release
```

**If user chooses edit:**
```bash
# Save to temp file
echo "$NOTES" > .release-notes.tmp
# Open in editor
${EDITOR:-nano} .release-notes.tmp
# Read edited content
# Re-display for confirmation
```

### Step 4: Prepare File Updates

**Update manifest.json:**
```bash
# Read current version
CURRENT=$(jq -r '.version' custom_components/qstream/manifest.json)

# Update to new version (e.g., "0.3.0" without v prefix)
jq --arg ver "0.3.0" '.version = $ver' custom_components/qstream/manifest.json > manifest.tmp
mv manifest.tmp custom_components/qstream/manifest.json
```

**Update/create CHANGELOG.md:**

If doesn't exist:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-26

[Release notes content]
```

If exists, prepend new section after header.

**Show diff to user:**
```bash
git diff custom_components/qstream/manifest.json CHANGELOG.md
```

### Step 5: Preview & Confirmation

**Display complete preview:**
```
=== Release Preview ===

Version: v0.3.0

Release Notes:
---
[Full markdown]
---

File Changes:
---
[Diff output]
---

Ready to proceed with release? (yes/no)
```

**Single confirmation point.** If user says no, restore files and exit cleanly.

### Step 6: Publish (Atomic Execution)

**Execute these steps sequentially:**

```bash
# 1. Commit version changes
git add custom_components/qstream/manifest.json CHANGELOG.md
git commit -m "chore: release v0.3.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 2. Create annotated tag
git tag -a v0.3.0 -m "Release v0.3.0

$(head -c 500 .release-notes.tmp)"

# 3. Push commit and tag
git push origin main
git push origin v0.3.0

# 4. Create GitHub Release
gh release create v0.3.0 \
  --title "v0.3.0" \
  --notes "$(cat .release-notes.tmp)" \
  --verify-tag

# 5. Verify release created
gh release view v0.3.0 --json url,tagName
```

**Display success:**
```
✅ Release v0.3.0 published successfully!

🔗 GitHub Release: https://github.com/bramd/qstream-ha/releases/tag/v0.3.0
🏷️  Git Tag: v0.3.0
📝 Changelog: Updated in CHANGELOG.md

Next steps:
- HACS will automatically detect the new release
- Users can update via HACS UI
```

**Clean up:**
```bash
rm -f .release-notes.tmp
```

## Error Recovery

### Network Failure During Push

```
Error: Failed to push tag v0.3.0

Recovery commands:
git push origin v0.3.0
gh release create v0.3.0 --title "v0.3.0" --notes-file .release-notes.tmp
```

### GitHub Release Creation Fails

```
Error: Tag pushed but GitHub Release creation failed

The tag v0.3.0 exists on remote. Create release manually:
gh release create v0.3.0 --title "v0.3.0" --notes-file .release-notes.tmp
```

**Don't re-push tag** (already exists on remote).

### First Release (No Tags)

- Default to v0.1.0
- Show all commits since repository creation
- Create initial CHANGELOG.md structure

### User Cancels at Preview

- No files committed
- No tags created
- Clean exit: "Release cancelled. No changes made."

## Red Flags - STOP Immediately

**Never proceed if:**
- ❌ Working directory not clean
- ❌ Not on main branch
- ❌ CI failing on main
- ❌ Local main behind origin
- ❌ Tag version already exists

**All of these mean:** Fix the issue first, then restart release process.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip pre-checks to "save time" | Pre-checks prevent mid-release failures. Always run. |
| Publish without preview | Preview catches errors before they're public. Always show. |
| Skip CHANGELOG.md | Users need release notes. Always update. |
| Use lightweight tag | Use annotated tag (-a) for better metadata. |
| Skip version override check | Duplicate tags cause errors. Always verify uniqueness. |

## Safety Guarantees

- **No partial states:** All file changes committed atomically
- **No orphaned tags:** Tag only created after commit succeeds
- **No duplicate versions:** Pre-check prevents tag collisions
- **Preview before publish:** Single review point before changes go live
- **Idempotent recovery:** Failed operations can be retried safely
