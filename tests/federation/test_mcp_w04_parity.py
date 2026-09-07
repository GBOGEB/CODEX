from datetime import datetime, timezone
from pathlib import Path
import pytest
from src.federation.mcp_sweep_services import SweepInputContract, SweepOutputContract, SweepFinding, TokenBoundaryGuard, TokenScope, SweepStateStore

def test_representative_contract_and_provenance():
    assert SweepInputContract(repo="GBOGEB/CODEX",max_prs=50).validate()==[]
    finding=SweepFinding("pr:1","github_pr","PR-1","follow-up",0.9,"proposed",("repo:GBOGEB/CODEX","pr:1"),datetime.now(timezone.utc).isoformat())
    assert SweepOutputContract("GBOGEB/CODEX",datetime.now(timezone.utc).isoformat(),near_misses=[finding]).validate()==[]

def test_adversarial_contract_rejects_invalid_repo_and_limit():
    issues=SweepInputContract(repo="not a repo",max_prs=0).validate()
    assert "repo must use owner/repo format" in issues
    assert "max_prs must be greater than zero" in issues

def test_adversarial_token_scope_is_fail_closed():
    guard=TokenBoundaryGuard()
    with pytest.raises(PermissionError): guard.get_token(TokenScope.GITHUB)
    guard.handshake(TokenScope.GITHUB,"token")
    assert guard.get_token(TokenScope.GITHUB)=="token"

def test_representative_ttl_dedupe(tmp_path:Path):
    now=datetime.now(timezone.utc); store=SweepStateStore(tmp_path/"state.json",ttl_days=30)
    assert store.should_include("pr:1",now)
    store.record("pr:1",now)
    assert not store.should_include("pr:1",now)

def test_adversarial_output_rejects_confidence_and_missing_provenance():
    bad=SweepFinding("bad","github_pr","PR-2","x",1.5,"proposed",(),datetime.now(timezone.utc).isoformat())
    issues=SweepOutputContract("GBOGEB/CODEX",datetime.now(timezone.utc).isoformat(),near_misses=[bad]).validate()
    assert any("invalid confidence" in x for x in issues)
    assert any("missing provenance" in x for x in issues)
