# QStream Release Skill Design

**Date:** 2025-10-26
**Purpose:** Design a project-specific skill to automate the QStream Home Assistant integration release process with safety checks, version management, and artifact creation.

## Overview

The `qstream:cutting-a-release` skill automates the complete release workflow for the QStream integration, following semantic versioning and creating all necessary release artifacts.

**Core Architecture: Atomic with Dry-Run**

Three-phase approach ensures all changes are prepared first, reviewed once, then executed atomically:

1. **Preparation Phase** - Gather information, prepare changes (no repository modifications)
2. **Preview Phase** - Show complete preview, single confirmation point
3. **Publishing Phase** - Execute atomically after confirmation

**Key Principle:** All changes prepared first, single review point, atomic execution. If user cancels, no repository state changed.

## Requirements

### Versioning Strategy
- **Semantic Versioning:** MAJOR.MINOR.PATCH (e.g., 0.1.0, 0.2.0, 1.0.0)
- **Auto-suggestion:** Calculate from conventional commits with user override option
- **Validation:** Check format and uniqueness before proceeding

### Release Artifacts
1. **Git tag** - Annotated tag (e.g., `v0.2.0`) marking the release commit
2. **GitHub Release** - Release with notes, automatic source archives
3. **manifest.json** - Updated version field
4. **CHANGELOG.md** - Updated/created with release notes

### Pre-Release Checks (All Required)
1. **CI workflows pass** - Verify latest run on main succeeded
2. **No uncommitted changes** - Working directory must be clean
3. **On main branch** - Must be on default branch
4. **Version not already tagged** - Prevent duplicate releases
5. **Remote sync** - Local main must be up-to-date with origin

### Release Notes
- **Hybrid approach:** Auto-generate from commits, present draft, allow editing
- **Conventional commits:** Parse for feat/fix/BREAKING/docs
- **PR linking:** Automatically include PR numbers from commit messages

## Architecture

### Phase 1: Preparation (No Repository Changes)

**1.1 Pre-Release Verification**

Run all safety checks before proceeding:

```bash
# Branch verification
git branch --show-current  # Must be 'main'

# Working directory status
git status --porcelain  # Must be empty

# CI workflow status
gh run list --branch main --limit 1 --json conclusion

# Remote sync check
git fetch origin main
git rev-list HEAD..origin/main --count  # Must be 0
```

**Failure Handling:** Stop immediately with clear error and remediation steps if any check fails.

**1.2 Version Suggestion**

Calculate suggested version from commit history:

```bash
# Find last release tag
git describe --tags --abbrev=0 --match "v*"
# If no tags: Start at v0.1.0

# Analyze commits since last tag
git log v0.1.0..HEAD --pretty=format:"%s"
```

**Version Bump Logic:**
- `BREAKING CHANGE:` or `!` → Major bump (0.1.0 → 1.0.0)
- `feat:` or `feat(...)` → Minor bump (0.1.0 → 0.2.0)
- `fix:` → Patch bump (0.1.0 → 0.1.1)
- Other types (docs, chore, ci, test) → No impact
- No conventional commits → Patch bump (default)

**Version Selection:**
```
Suggested version: v0.2.0 (minor bump)
Reason: Found 2 features, 1 fix since v0.1.0

Commits analyzed:
- feat: add Dutch translation support
- docs: add brand assets design

Accept v0.2.0 or specify different version?
```

User can override with any valid semver. Validate format and check uniqueness:
```bash
git tag --list "v{user_version}"  # Must not exist
```

**1.3 Release Notes Generation**

Auto-generate from conventional commits:

```bash
git log v0.1.0..HEAD --pretty=format:"%s|||%b"
```

**Categorization:**
- **Breaking Changes** - `BREAKING CHANGE:` in body or `!` in type
- **Features** - `feat:` or `feat(...)`
- **Bug Fixes** - `fix:` or `fix(...)`
- **Documentation** - `docs:`
- **Other** - ci, chore, test, refactor

**Markdown Structure:**
```markdown
## What's Changed

### Breaking Changes
- Description from BREAKING CHANGE message

### Features
- Add Dutch translation support (#3)
- New demand control switch

### Bug Fixes
- Fix connection timeout handling (#2)

### Documentation
- Add brand assets design document

**Full Changelog**: https://github.com/bramd/qstream-ha/compare/v0.1.0...v0.2.0
```

**PR Linking:** Extract `(#123)` patterns from commit messages automatically.

**1.4 Artifact Preparation**

Prepare file updates in-memory (no writes yet):

**manifest.json:**
```bash
# Read current manifest
# Update "version" field: "0.1.0" → "0.2.0"
# Preserve all other fields
```

Use `jq` or Python json module. Only modify `version` field, maintain formatting.

**CHANGELOG.md:**

If doesn't exist, create with structure:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-26
[Generated release notes content]

## [0.1.0] - [Previous date]
- Initial release
```

If exists, prepend new section after header, keep existing entries intact.

### Phase 2: Preview & Confirmation

**2.1 Present Complete Preview**

Show all prepared changes:

```
=== Release Preview ===

Version: v0.2.0

Release Notes:
---
[Full generated markdown]
---

File Changes:
---
[git diff preview of manifest.json and CHANGELOG.md]
---

Options:
1. Proceed with release
2. Edit release notes
3. Cancel
```

**2.2 Edit Workflow (Optional)**

If user chooses edit:
```bash
# Write notes to temp file
echo "$NOTES" > .release-notes.tmp

# Open in editor
${EDITOR:-nano} .release-notes.tmp

# Read back edited content
# Re-display for confirmation
```

**2.3 Single Confirmation Point**

All-or-nothing decision before any repository changes.

### Phase 3: Publishing (Atomic Execution)

Execute sequentially after confirmation:

**3.1 Commit Changes**
```bash
git add custom_components/qstream/manifest.json CHANGELOG.md
git commit -m "chore: release v0.2.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**3.2 Create Annotated Tag**
```bash
git tag -a v0.2.0 -m "Release v0.2.0

[First 500 chars of release notes]"
```

Use annotated tag (not lightweight) for better Git metadata.

**3.3 Push to Remote**
```bash
git push origin main
git push origin v0.2.0
```

Push commit first, then tag (ensures commit exists before tag reference).

**3.4 Create GitHub Release**
```bash
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes "[Full release notes markdown]" \
  --verify-tag
```

**3.5 Verify Success**
```bash
gh release view v0.2.0 --json url,tagName,name
```

Display success message:
```
✅ Release v0.2.0 published successfully!

🔗 GitHub Release: https://github.com/bramd/qstream-ha/releases/tag/v0.2.0
🏷️  Git Tag: v0.2.0
📝 Changelog: Updated in CHANGELOG.md

Next steps:
- HACS will automatically detect the new release
- Users can update via HACS UI
```

## Error Handling

### Common Failure Scenarios

**1. Network Failures During Push**
```
Error: Failed to push tag v0.2.0

Recovery commands:
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes-file .release-notes.tmp
```

Save release notes to `.release-notes.tmp` for manual recovery.

**2. GitHub Release Creation Fails**
```
Error: Tag pushed but GitHub Release creation failed

The tag v0.2.0 exists on remote. Create release manually:
gh release create v0.2.0 --title "v0.2.0" --notes-file .release-notes.tmp
```

Don't re-push tag (already exists).

**3. First Release (No Previous Tags)**
- Default to v0.1.0
- Show all commits since repository creation
- Create initial CHANGELOG.md structure

**4. Multiple Commits Without Conventional Format**
- Still calculate patch bump (default)
- Include all commits in "Other Changes" section
- Suggest: "Consider using conventional commits for better release notes"

**5. User Cancels at Confirmation**
- No files modified
- No git operations performed
- Clean exit: "Release cancelled. No changes made."

### Safety Guarantees

- **No partial states:** All file changes committed atomically
- **No orphaned tags:** Tag only created after commit succeeds
- **No duplicate versions:** Pre-check prevents tag collisions
- **Idempotent recovery:** Failed operations can be retried safely

## Implementation Details

### File Locations

**Skill file:**
```
.claude/commands/qstream/cutting-a-release.md
```

**Invocation:**
```
/qstream:cutting-a-release
```

No arguments needed - skill guides through entire process interactively.

### Dependencies

**Required tools:**
- `git` - Version control operations
- `gh` - GitHub CLI for releases and CI checks
- `jq` or Python - JSON manipulation for manifest.json

**All tools already available in QStream project environment.**

### Skill Structure

```markdown
# Cutting a QStream Release

## Overview
[Brief description of skill purpose]

## Process

### Step 1: Pre-Release Checks
[Verification commands and failure handling]

### Step 2: Version Calculation
[Version suggestion logic and user override]

### Step 3: Release Notes Generation
[Commit parsing and categorization]

### Step 4: Preview & Confirmation
[Show complete preview, handle edits]

### Step 5: Publishing
[Atomic execution steps]

### Step 6: Verification
[Success confirmation and next steps]

## Error Recovery
[Common failures and manual recovery commands]
```

## Testing Strategy

### Manual Testing (Before First Use)

1. **Dry-run on test repository:**
   - Fork qstream-ha to test repo
   - Create dummy commits with conventional format
   - Run skill, verify all artifacts created correctly
   - Check GitHub Release appears properly

2. **Edge case testing:**
   - Test with no previous tags (first release)
   - Test with non-conventional commits
   - Test cancellation at confirmation (verify no changes)
   - Test version override

3. **Failure simulation:**
   - Disconnect network during push (test recovery commands)
   - Make working directory dirty (test pre-check)
   - Try releasing from non-main branch (test pre-check)

### Validation Checklist

After skill creates release:
- [ ] Git tag exists and is annotated
- [ ] manifest.json version updated correctly
- [ ] CHANGELOG.md has new entry with correct format
- [ ] GitHub Release created with proper notes
- [ ] Commit message follows format
- [ ] All changes pushed to remote
- [ ] HACS can detect new version

## Benefits

### For Maintainers
- **Consistency:** Every release follows same process
- **Safety:** Pre-checks prevent common mistakes
- **Speed:** Automate manual steps (changelog, tagging, GitHub Release)
- **Documentation:** Changelog automatically maintained

### For Users
- **Reliability:** Releases always have complete artifacts
- **Visibility:** Clear release notes explain changes
- **HACS Integration:** Automatic version detection for updates

### For Project
- **Professional:** Consistent versioning and release notes
- **Traceable:** Every release has tag, commit, and changelog entry
- **Recoverable:** Clear error messages and manual recovery steps

## Future Enhancements

### Possible Additions (YAGNI - Only If Needed)

1. **Automatic dependency updates:**
   - Check for outdated dependencies before release
   - Suggest running Dependabot before release

2. **Release branch support:**
   - Support releasing from release/v0.2.x branches
   - Cherry-pick fixes to release branches

3. **Pre-release versions:**
   - Support beta/rc versions (v0.2.0-beta.1)
   - Tag as pre-release in GitHub

4. **Automated testing trigger:**
   - Wait for CI to pass after tag push
   - Don't create GitHub Release until CI succeeds

**Current design excludes these to keep skill simple and focused.**

## References

- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
