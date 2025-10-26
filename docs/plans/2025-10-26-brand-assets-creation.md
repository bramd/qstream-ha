# QStream Brand Assets Creation and Submission

**Date:** 2025-10-26
**Purpose:** Create and submit brand assets (icons and logos) to the Home Assistant brands repository for the QStream custom integration.

## Overview

This document outlines the automated process for converting the BUVA logo SVG into properly formatted PNG assets that meet Home Assistant's brand repository requirements, and submitting them via pull request.

## Requirements

### Home Assistant Brands Repository Requirements

**General Image Requirements:**
- Format: PNG only
- Compression: Properly optimized (lossless preferred)
- Progressive/Interlaced preferred
- Transparency preferred
- Trimmed with minimum empty space
- Optimized for white background (no dark variants needed initially)

**Icon Requirements:**
- Aspect ratio: 1:1 (square)
- Sizes: 256x256px (`icon.png`) and 512x512px (`icon@2x.png`)

**Logo Requirements:**
- Landscape preferred
- Aspect ratio: Respect brand's natural ratio
- Shortest side: 256px for normal, 512px for @2x version

**Repository Structure:**
- Custom integrations go in: `custom_integrations/{domain}/`
- Domain must match integration's `manifest.json` domain
- Files: `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png`

## Architecture

### Components

1. **Source SVG Preparation**
   - BUVA logo SVG (123x33 viewBox, horizontal wordmark)
   - Stored in parent directory: `../buva_source.svg`

2. **SVG Variant Generator** (Python script)
   - Creates square icon variant with padding
   - Creates landscape logo variant (trimmed)
   - Uses built-in `xml.etree.ElementTree` library

3. **PNG Converter** (Docker + ImageMagick)
   - Docker image: `dpokidov/imagemagick`
   - Converts SVGs to PNG at required sizes
   - Uses transparent background and high density (300 DPI)

4. **PNG Optimizer** (Docker + optipng)
   - Docker image: `pstauffer/optipng`
   - Lossless compression with maximum optimization (-o7)

5. **Brands Repository Submission**
   - Fork `home-assistant/brands`
   - Create PR with assets in `custom_integrations/qstream/`

### File Structure

```
C:/Users/bram/src/
├── qstream-ha/                      # Integration repo (clean, no scripts)
│   └── docs/plans/                  # This design doc
├── create_brand_assets.py           # Temporary utility script
├── buva_source.svg                  # Source SVG
├── brands_assets/                   # Generated PNG output
│   ├── icon.png                     # 256x256
│   ├── icon@2x.png                  # 512x512
│   ├── logo.png                     # Landscape, 256px shortest side
│   └── logo@2x.png                  # Landscape, 512px shortest side
└── brands/                          # Cloned brands repo
    └── custom_integrations/qstream/
        ├── icon.png
        ├── icon@2x.png
        ├── logo.png
        └── logo@2x.png
```

## Design Details

### SVG Variant Generation

**Icon Variant (Square):**
- Original BUVA wordmark: 123x33 viewBox
- New square canvas: 133x133 (adds padding for readability)
- Center wordmark horizontally and vertically
- Transparent background
- Output: `buva_icon.svg`

**Logo Variant (Landscape):**
- Use original BUVA SVG dimensions (123x33)
- Natural aspect ratio ~3.7:1
- Ensure proper trimming
- Output: `buva_logo.svg`

**Implementation:**
```python
import xml.etree.ElementTree as ET

# Parse original SVG
tree = ET.parse('../buva_source.svg')
root = tree.getroot()

# For icon: Modify viewBox to square with padding
root.set('viewBox', '0 0 133 133')
# Add transform to center the original content
# g = ET.SubElement(root, 'g', transform='translate(5, 50)')
# Move existing content into g

# For logo: Keep original viewBox, ensure trimming
```

### PNG Conversion with Docker

**Docker Commands:**

Icon conversions:
```bash
docker run --rm -v ${PWD}:/work dpokidov/imagemagick \
  -background transparent -density 300 \
  /work/buva_icon.svg -resize 256x256 /work/icon.png

docker run --rm -v ${PWD}:/work dpokidov/imagemagick \
  -background transparent -density 300 \
  /work/buva_icon.svg -resize 512x512 /work/icon@2x.png
```

Logo conversions (maintain aspect ratio):
```bash
docker run --rm -v ${PWD}:/work dpokidov/imagemagick \
  -background transparent -density 300 \
  /work/buva_logo.svg -resize x256 /work/logo.png

docker run --rm -v ${PWD}:/work dpokidov/imagemagick \
  -background transparent -density 300 \
  /work/buva_logo.svg -resize x512 /work/logo@2x.png
```

**Parameters explained:**
- `--rm`: Remove container after execution
- `-v ${PWD}:/work`: Mount current directory as /work in container
- `-background transparent`: Preserve transparency
- `-density 300`: High-quality rendering from vector
- `-resize 256x256`: Exact dimensions for icon
- `-resize x256`: Scale to 256px height, maintain aspect ratio for logo

### PNG Optimization

**Optimization command:**
```bash
docker run --rm -v ${PWD}:/work pstauffer/optipng /work/*.png
```

**Settings:**
- Uses optipng's default optimization level (or specify -o7 for maximum)
- Lossless compression
- Reduces file size while maintaining quality

## Automation Script

**Script:** `../create_brand_assets.py`

**Dependencies:**
- Python 3.11+ (no external packages needed)
- Docker installed and running

**Script workflow:**
1. Check Docker availability
2. Save source SVG to `../buva_source.svg`
3. Generate SVG variants (`buva_icon.svg`, `buva_logo.svg`)
4. Pull Docker images if needed
5. Convert SVGs to PNGs (4 files)
6. Optimize PNGs
7. Create `../brands_assets/` directory
8. Move PNGs to output directory
9. Print summary and next steps

**Error handling:**
- Check Docker is running
- Verify output file dimensions
- Report file sizes
- Display clear error messages

**Output:**
```
✓ Created buva_icon.svg (square variant)
✓ Created buva_logo.svg (landscape variant)
✓ Converting to PNG...
  - icon.png (256x256) - 15.2 KB
  - icon@2x.png (512x512) - 45.8 KB
  - logo.png (944x256) - 18.4 KB
  - logo@2x.png (1888x512) - 55.1 KB
✓ Optimized with optipng
✓ Assets ready in ../brands_assets/

Next steps:
1. Fork home-assistant/brands on GitHub
2. git clone https://github.com/bramd/brands.git ../brands
3. cd ../brands && git checkout -b add-qstream-brand
4. mkdir -p custom_integrations/qstream
5. Copy PNG files from ../brands_assets/ to custom_integrations/qstream/
6. git add custom_integrations/qstream/
7. git commit -m "Add QStream brand assets"
8. git push origin add-qstream-brand
9. Create PR to home-assistant/brands
```

## Submission Process

### Step 1: Fork and Clone

1. Fork `home-assistant/brands` repository on GitHub to your account
2. Clone your fork:
   ```bash
   cd ../  # From qstream-ha directory
   git clone https://github.com/bramd/brands.git
   cd brands
   ```
3. Create feature branch:
   ```bash
   git checkout -b add-qstream-brand
   ```

### Step 2: Copy Assets

1. Create domain directory:
   ```bash
   mkdir -p custom_integrations/qstream
   ```
2. Copy generated PNGs:
   ```bash
   cp ../brands_assets/*.png custom_integrations/qstream/
   ```
3. Verify files:
   ```bash
   ls -lh custom_integrations/qstream/
   ```

### Step 3: Commit and Push

1. Stage files:
   ```bash
   git add custom_integrations/qstream/
   ```
2. Commit:
   ```bash
   git commit -m "Add QStream brand assets

   - Add icon and logo for QStream custom integration
   - Domain: qstream
   - Integration: https://github.com/bramd/qstream-ha
   - All images meet HA brand requirements (PNG, optimized, transparent)"
   ```
3. Push:
   ```bash
   git push origin add-qstream-brand
   ```

### Step 4: Create Pull Request

**PR Title:** `Add QStream brand assets`

**PR Description:**
```markdown
## Summary
Adding brand assets for the QStream custom integration.

## Details
- **Domain:** `qstream`
- **Integration repository:** https://github.com/bramd/qstream-ha
- **Assets included:**
  - icon.png (256x256)
  - icon@2x.png (512x512)
  - logo.png (landscape, 256px shortest side)
  - logo@2x.png (landscape, 512px shortest side)

## Checklist
- [x] All images are PNG format
- [x] Images are properly compressed and optimized
- [x] Images use transparent background
- [x] Images are trimmed with minimal whitespace
- [x] Icon is square (1:1 aspect ratio)
- [x] Logo maintains brand's natural aspect ratio
- [x] Domain matches integration's manifest.json
```

### Timeline Expectations

- **Review time:** Typically 1-7 days
- **Feedback:** Maintainers may request adjustments to images
- **Merge:** Once approved, images available via HA CDN
- **HACS submission:** Can proceed once brands PR is merged

## Post-Submission Cleanup

After the brands PR is merged, you can clean up temporary files:

```bash
cd ../qstream-ha  # Return to integration repo
rm ../create_brand_assets.py
rm ../buva_source.svg
rm -rf ../brands_assets/
# Optionally delete brands clone: rm -rf ../brands/
```

## Success Criteria

1. ✅ All 4 PNG files generated correctly
2. ✅ Files meet size requirements (256x256, 512x512, etc.)
3. ✅ Images are optimized and under reasonable file sizes
4. ✅ PR created and submitted to brands repository
5. ✅ PR passes automated checks
6. ✅ PR approved and merged by HA maintainers
7. ✅ HACS action validation passes (brands check)

## Notes

- This is a one-time process per integration
- Dark variants (`dark_*.png`) can be added later if needed
- Symlinks not allowed in custom_integrations folder
- Domain name must exactly match integration's manifest.json
- Custom integrations must not use Home Assistant branded imagery
