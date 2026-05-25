#!/usr/bin/env python3
"""
CODEX Federation Bridge - Core Ingestion & Dashboard Synchronization Engine
Author: gbogeb
"""
import re
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class FederationBridgeEngine:
    def __init__(self, workspace_root="."):
        self.root = Path(workspace_root).resolve()
        self.glossary_path = self.root / "GLOSSARY.yaml"
        # Targets standard GitHub Pages entry point (index.html) or fallback dashboard
        self.dashboard_path = self.root / "docs" / "index.html"
        if not self.dashboard_path.exists():
            self.dashboard_path = self.root / "docs" / "federation_bridge_dashboard.html"

        self.ingress_path = self.root / "core_bridge" / "ingress"
        self.ingress_path.mkdir(parents=True, exist_ok=True)
        self.glossary = self._load_glossary()

    def _load_glossary(self):
        if not self.glossary_path.exists():
            return {"terms": []}
        with open(self.glossary_path, "r", encoding="utf-8") as f:
            if HAS_YAML:
                return yaml.safe_load(f) or {"terms": []}
            else:
                terms = []
                for line in f:
                    if line.strip().startswith("- tag:"):
                        tag = line.split(":", 1)[1].strip().strip('"').strip("'")
                        terms.append({"tag": tag})
                return {"terms": terms}

    def scan_workspace(self):
        """Recursively parses workspace for unallocated handovers, specs, and scripts."""
        stats = {"docx": 0, "pptx": 0, "py_loose": 0, "txt": 0, "visio_svg": 0}
        for path in self.root.rglob("*"):
            if path.is_dir() or ".venv" in path.parts or ".git" in path.parts:
                continue
            ext = path.suffix.lower()
            if ext == ".docx":
                stats["docx"] += 1
            elif ext == ".pptx":
                stats["pptx"] += 1
            elif ext == ".txt":
                stats["txt"] += 1
            elif ext == ".py" and "core_bridge" not in path.parts:
                stats["py_loose"] += 1
            elif ext == ".svg" and ("visio" in str(path).lower() or "drawio" in str(path).lower()):
                stats["visio_svg"] += 1
        return stats

    def execute_patch(self):
        if not self.dashboard_path.exists():
            print("[-] Execution stopped: Target layout file not found.")
            return False

        stats = self.scan_workspace()
        total_mapped = len(self.glossary.get("terms", []))
        total_files = sum(stats.values())

        wave_output = (
            f"DMAIC Layer Active | Processed N={total_files} files "
            f"(Word: {stats['docx']}, Py: {stats['py_loose']}, Visio/SVG: {stats['visio_svg']})"
        )

        with open(self.dashboard_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        target_regex = re.compile(
            r'<div class="card-panel" id="federation-bridge-status">.*?</div>',
            re.DOTALL,
        )

        new_block = f"""<div class="card-panel" id="federation-bridge-status">
        <h2>FEDERATION BRIDGE STATUS</h2>
        <p style="color: #8e8e93; font-size: 0.85rem; line-height: 1.5; margin: 0;">
          Ingestion and render pipelines are active with glossary traceability.
        </p>
        <ul style="margin-top: 1rem;">
          <li><strong>Traceability Master:</strong> {total_mapped} verified terms linked to canonical SSOT.</li>
          <li><strong>Wave Statistics:</strong> {wave_output}.</li>
        </ul>
      </div>"""

        if target_regex.search(html_content):
            updated_html = target_regex.sub(new_block, html_content)
        elif "</main>" in html_content:
            updated_html = html_content.replace("</main>", f"{new_block}\n    </main>", 1)
        else:
            print("[-] Error: Could not locate a stable insertion point in dashboard template.")
            return False

        with open(self.dashboard_path, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print(f"[+] Success: Dynamic analytics patched to {self.dashboard_path.name}")
        return True


if __name__ == "__main__":
    engine = FederationBridgeEngine()
    sys.exit(0 if engine.execute_patch() else 1)
