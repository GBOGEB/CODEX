# STYLE GUIDE

# ABACUS_RENDER_PIPELINE

## Theme Light

```yaml
theme_light:
  canvas: '#F4F2EE'
  title_bar: '#5B2E91'
  title_text: '#FFFFFF'
  card:
    background: '#FFFFFF'
    text: '#1F2430'
```

---

# Theme Dark

```yaml
theme_dark:
  canvas: '#181421'
  title_bar: '#3A2460'
  title_text: '#FFFFFF'
  card:
    background: '#241D33'
    text: '#F5F2FF'
```

---

# Semantic Cards

## Warning

```yaml
warning:
  light:
    background: '#F5E8A8'
    text: '#2B2111'

  dark:
    background: '#3B2A00'
    border: '#C89B00'
    text: '#FFE9A3'
```

## Decision

```yaml
decision:
  dark:
    background: '#214F36'
    text: '#DDFBE8'
```

## SSOT

```yaml
ssot:
  dark:
    background: '#3B2063'
    text: '#E5D2FF'
```

---

# Typography

```yaml
fonts:
  title:
    family: "Aptos, 'Segoe UI', Calibri, Arial, sans-serif"
    size: 24
    weight: 700

  section:
    family: "Aptos, 'Segoe UI', Calibri, Arial, sans-serif"
    size: 18
    weight: 600

  body:
    family: "Aptos, 'Segoe UI', Calibri, Arial, sans-serif"
    size: 13

  technical:
    family: "Consolas, 'Liberation Mono', 'Courier New', monospace"
    size: 12
```

---

# Renderer Principle

Semantic meaning must survive:

- dark mode
- PDF export
- PPTX export
- HTML rendering
- GitHub Pages snapshots

Theme transforms are semantic, not inversion-based.
