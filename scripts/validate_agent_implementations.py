#!/usr/bin/env python3
"""Validate agent capabilities against implementation map."""

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
    """Validate agent implementations."""
    print("=== W000 Agent Implementation Validation ===\n")
    
    # Load agent registry
    agent_reg_path = ROOT / "governance/agent_registry.yml"
    if not agent_reg_path.exists():
        print(f"❌ Agent registry not found: {agent_reg_path}")
        return 1
    
    agent_reg = load_yaml(agent_reg_path)
    
    # Load agent implementation map
    impl_map_path = ROOT / "governance/agent_implementation_map.yml"
    if not impl_map_path.exists():
        print(f"❌ Agent implementation map not found: {impl_map_path}")
        return 1
    
    impl_map = load_yaml(impl_map_path)
    
    print(f"✅ Loaded agent registry: {agent_reg_path}")
    print(f"✅ Loaded implementation map: {impl_map_path}\n")
    
    # Cross-validate agents
    registry_agents = {a["id"]: a for a in agent_reg.get("agents", [])}
    mapped_agents = {m["agent_id"]: m for m in impl_map.get("mappings", [])}
    
    all_ok = True
    
    # Check that all registry agents have mappings
    print("Agent Registration Check:\n")
    for agent_id, agent_info in registry_agents.items():
        if agent_id in mapped_agents:
            print(f"  ✅ {agent_id}: mapping found")
        else:
            print(f"  ❌ {agent_id}: NO MAPPING")
            all_ok = False
    
    print("\nCapability Implementation Status:\n")
    
    # Validate implementation paths
    total_caps = 0
    implemented_caps = 0
    scaffold_caps = 0
    
    for mapping in impl_map.get("mappings", []):
        agent_id = mapping["agent_id"]
        print(f"  [{agent_id}]")
        
        for cap in mapping.get("capabilities", []):
            total_caps += 1
            cap_name = cap["capability"]
            impl_path = cap.get("implementation")
            status = cap.get("status", "unknown")
            
            if impl_path:
                impl_file = ROOT / impl_path
                if impl_file.exists():
                    print(f"    ✅ {cap_name}: {status} ({impl_path})")
                    implemented_caps += 1
                else:
                    print(f"    ⚠️  {cap_name}: {status} (FILE NOT FOUND: {impl_path})")
                    all_ok = False
            else:
                print(f"    🏗️  {cap_name}: {status} (not yet implemented)")
                scaffold_caps += 1
        
        print()
    
    # Summary statistics
    print("=== Implementation Summary ===\n")
    print(f"  Total agents: {len(registry_agents)}")
    print(f"  Mapped agents: {len(mapped_agents)}")
    print(f"  Total capabilities: {total_caps}")
    print(f"  Implemented: {implemented_caps} ({implemented_caps/total_caps*100:.1f}%)")
    print(f"  Scaffold: {scaffold_caps} ({scaffold_caps/total_caps*100:.1f}%)")
    
    # Check statistics match
    stats = impl_map.get("statistics", {})
    expected_total = stats.get("total_capabilities", 0)
    expected_impl = stats.get("implemented_capabilities", 0)
    
    if total_caps != expected_total:
        print(f"\n⚠️  Statistics mismatch: counted {total_caps} capabilities, map claims {expected_total}")
    
    if implemented_caps != expected_impl:
        print(f"⚠️  Statistics mismatch: counted {implemented_caps} implemented, map claims {expected_impl}")
    
    print("\n=== Agent Implementation Validation Complete ===")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
