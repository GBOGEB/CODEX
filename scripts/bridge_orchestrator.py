#!/usr/bin/env python3
"""Bridge orchestrator - validates federation links against bridge configs."""

from __future__ import annotations

from pathlib import Path
import sys
import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    """Load YAML file safely."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    """Validate federation links against available bridge configurations."""
    print("=== W000 Bridge Orchestration Check ===\n")
    
    # Load W000 federation registry
    fed_reg_path = ROOT / "governance/federation_registry.yml"
    if not fed_reg_path.exists():
        print(f"❌ Federation registry not found: {fed_reg_path}")
        return 1
    
    fed_reg = load_yaml(fed_reg_path)
    
    # Load bridge manifest
    bridge_manifest_path = ROOT / "bridge_manifest.yaml"
    if not bridge_manifest_path.exists():
        print(f"⚠️  Bridge manifest not found: {bridge_manifest_path}")
        bridge_manifest = None
    else:
        bridge_manifest = load_yaml(bridge_manifest_path)
        print(f"✅ Bridge manifest loaded: {bridge_manifest_path}\n")
    
    # Validate each federation link
    all_ok = True
    federation_links = fed_reg.get("federation_links", [])
    
    if not federation_links:
        print("⚠️  No federation links defined in registry")
        return 0
    
    print("Federation Link Validation:\n")
    for link in federation_links:
        link_id = link.get("id", "unknown")
        link_purpose = link.get("purpose", "N/A")
        link_provider = link.get("provider", "N/A")
        
        # Check for corresponding bridge config
        # office-link → office_bridge.yml
        # diagram-link → diagram_bridge.yml
        bridge_name = link_id.replace("-link", "_bridge")
        bridge_file = ROOT / f"bridges/{bridge_name}.yml"
        
        print(f"  [{link_id}]")
        print(f"    Purpose: {link_purpose}")
        print(f"    Provider: {link_provider}")
        
        if bridge_file.exists():
            bridge_config = load_yaml(bridge_file)
            print(f"    Status: ✅ Bridge config found")
            print(f"    Config: {bridge_file}")
            
            # Validate bridge has required fields
            if "bridge" not in bridge_config:
                print(f"    Warning: Bridge config missing 'bridge' key")
                all_ok = False
        else:
            print(f"    Status: ⚠️  No bridge config")
            print(f"    Expected: {bridge_file}")
            # Not a failure - just indicates scaffold
        
        print()
    
    # Summary
    if bridge_manifest:
        repos = bridge_manifest.get("federation_bridge", {}).get("repos", {})
        print(f"\nBridge Manifest Summary:")
        print(f"  Repos tracked: {len(repos)}")
        for repo_name, repo_info in repos.items():
            print(f"    - {repo_name}: {repo_info.get('role', 'N/A')}")
    
    print("\n=== Bridge Orchestration Check Complete ===")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
