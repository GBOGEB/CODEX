#!/usr/bin/env bash
# ==============================================================================
# FEDERATION BRIDGE GO-LIVE INITIALIZATION RUNTIME
# ==============================================================================
set -e

echo "[1/6] Synchronizing Local Workspace Environment and Virtual Paths..."
# Only activate venv if it exists
if [ -d .venv ]; then
    source .venv/bin/activate || echo "[!] VENV activation failed; relying on runtime environment defaults"
else
    echo "[!] No .venv found; using system Python"
fi

# Ensure directory structure exists
mkdir -p core_bridge/ingress docs/rendered_outputs docs/visio

# Note: The federation_bridge_dashboard.html should remain separate from index.html
# as index.html is the canonical entrypoint per MANIFEST.json
echo "[*] Keeping federation_bridge_dashboard.html as separate diagnostic dashboard..."

echo "[2/6] Rendering Executable Permissions onto Ingestion Core Components..."
chmod +x core_bridge/absorb.py
chmod +x core_bridge/render.py

echo "[3/6] Depositing Testing Samples for Process Ingestion Wave..."
cat > core_bridge/ingress/sample_spec.txt << 'EOF'
# MINERVA QPS Test Entry
- Component Tag: QPLANT_HE_REFRIG
---
# Slide Content Block
This is a test specification for the Federation Bridge ingestion system.
EOF

echo "[4/6] Triggering Self-Smoke Test Execution..."
python3 core_bridge/absorb.py

echo "[5/6] Verifying Multi-Format Compiler Layout Matrix..."
python3 core_bridge/render.py core_bridge/ingress/sample_spec.txt html
python3 core_bridge/render.py core_bridge/ingress/sample_spec.txt sheet

echo "[6/6] Running CI validation checks..."
python3 scripts/check_manifest.py
python3 scripts/check_globs.py
python3 scripts/check_stale.py
python3 scripts/check_links.py

echo ""
echo "[+] Federation Bridge initialization complete!"
echo "    - GLOSSARY.yaml: Canonical metadata SSOT"
echo "    - core_bridge/absorb.py: Ingestion engine"
echo "    - core_bridge/render.py: Multi-format exporter"
echo "    - docs/federation_bridge_dashboard.html: Updated with live stats"
echo ""
echo "Ready for deployment. Execute 'git push' to finalize changes."
