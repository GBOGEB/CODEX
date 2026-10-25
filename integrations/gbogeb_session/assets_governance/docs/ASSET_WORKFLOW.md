# Asset Workflow Guide

> End-to-end process for adding, validating, and deploying visual assets

## Workflow Overview

```
 ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │  Create  │ →  │ Validate │ →  │  Clean   │ →  │  Track   │ →  │  Deploy  │
 │  Asset   │    │  Asset   │    │  SVG     │    │ Lineage  │    │  Bundle  │
 └─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

## Step 1: Create the Asset

Place your SVG/PNG/DrawIO file in `assets/canonical/`:

```bash
cp my_diagram.svg assets/canonical/
```

**SVG Requirements:**
- Must include a `viewBox` attribute
- Must include a `<title>` element (accessibility)
- Recommended max size: 500 KB

## Step 2: Validate

```bash
python src/asset_validator.py --verify assets/canonical/my_diagram.svg
```

This checks:
- File extension is allowed (.svg, .png, .drawio, .jpg, .pdf)
- File size within limits
- SHA256 hash computed
- SVG-specific: viewBox present, `<title>` present

## Step 3: Clean SVG

```bash
python src/svg_cleaner.py assets/canonical/my_diagram.svg \
  --output-dir assets/compiled/ --prefix gbc
```

The cleaner:
1. Removes XML comments
2. Strips editor namespaces (Inkscape, Illustrator, Sketch)
3. Removes editor-specific attributes and elements
4. Normalizes the viewBox
5. Ensures `<title>` is present
6. Injects governance IDs (`gbc-rect-001`, etc.)

## Step 4: Track Lineage

```bash
python src/lineage_tracker.py --add assets/canonical/my_diagram.svg \
  --category svg_diagram --tags cryogenic engineering
```

This creates/updates `lineage_manifest.json` with:
- SHA256 hash for integrity
- File metadata (size, MIME type)
- Category and tags
- Timestamps and git commit

## Step 5: Register in Visual Data

Add your asset to `config/visual_data.yaml`:

```yaml
assets:
  - id: "GBC-ASSET-003"
    filename: "my_diagram.svg"
    title: "My Engineering Diagram"
    category: "engineering_diagram"
    # ...
```

## Step 6: Commit & Push

```bash
git add assets/ config/ lineage_manifest.json
git commit -m "feat: add my_diagram.svg engineering schematic"
git push origin feature/add-diagram
```

## Step 7: CI/CD

The push triggers:
1. **Asset Ingestion** — validates all assets, cleans SVGs
2. **Archive & Deploy** — builds bundle, deploys gallery

## Batch Processing

Process all assets at once:

```bash
# Validate all
python src/asset_validator.py --input-dir assets/canonical/

# Clean all
python src/svg_cleaner.py --input-dir assets/canonical/ --output-dir assets/compiled/

# Track all
for f in assets/canonical/*.svg; do
  python src/lineage_tracker.py --add "$f" --category svg_diagram
done

# Verify
python src/lineage_tracker.py --validate
python src/lineage_tracker.py --verify-hashes
python src/lineage_tracker.py --status
```
