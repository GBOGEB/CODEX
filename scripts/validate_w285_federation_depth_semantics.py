import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "federation/w285/CODEX_W285_FEDERATION_DEPTH_SEMANTIC_REVIEW_v0.1.json"

EXPECTED_GUARDS = {
    "FUNCTION_IDENTITY_NE_ATOM_CREDIT",
    "ONE_ATOM_MAX_ONE_NUMERATOR_CREDIT",
    "UNOBSERVED_FUNCTION_NE_ZERO_DEPTH",
    "BREADTH_CARRIES_UNCOVERED_FUNCTION_PENALTY",
    "PEN_IS_GOVERNED_INDEX_NOT_ENGINEERING_OR_COMPLIANCE_SCORE",
    "SOURCE_TOPOLOGY_AUTHORITY_REMAINS_PIPELINE_AUTOMATION_HUB",
    "QPS_CHILD_DISPOSITION_AUTHORITY_REMAINS_CRYOPLANT",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate() -> bool:
    d = json.loads(P.read_text(encoding="utf-8"))
    require(d.get("schema") == "codex-w285-federation-depth-semantic-review/v0.1", "schema mismatch")
    require(d.get("disposition") == "ACCEPT_BOUNDED_CURRENT_USE_ATOM_MODEL", "disposition mismatch")
    source = d.get("source") or {}
    require(source.get("repo") == "GBOGEB/cryoplant-project", "source repo mismatch")
    require(source.get("pr") == 1490, "source PR mismatch")
    require(source.get("head") == "f732bac39d9a92ab296982f08ca17185ec51812f", "source head mismatch")
    require(source.get("depth_blob") == "691680cdf11289142b402a0ae02c95d46a246473", "depth blob mismatch")
    require(source.get("topology_blob") == "df0ee845697578cd644691b81eafb2465249d772", "topology blob mismatch")

    findings = d.get("semantic_findings") or {}
    require(findings.get("categories_mixed") is False, "categories mixed")
    require(findings.get("bounded_sample_depth_reused") is False, "bounded sample depth reused")
    require(findings.get("uncovered_function_zero_imputation") is False, "uncovered function zero imputation")
    require(findings.get("equal_function_weighting") == "ACCEPTED_FOR_PEN_INDEX", "equal-function weighting guard missing")
    require(findings.get("pooled_atom_ratio") == "DESCRIPTIVE_ONLY_NOT_D", "pooled diagnostic guard missing")

    guards = d.get("accepted_guards")
    require(isinstance(guards, list), "accepted_guards must be a list")
    require(set(guards) == EXPECTED_GUARDS, "accepted guard set mismatch")
    require("SOURCE_TOPOLOGY_AUTHORITY_REMAINS_PIPELINE_AUTOMATION_HUB" in guards, "source topology authority guard missing")
    require("QPS_CHILD_DISPOSITION_AUTHORITY_REMAINS_CRYOPLANT" in guards, "QPS child authority guard missing")

    require(d.get("measurement") == {"B": 1 / 3, "D": 0.6, "PEN": 0.2}, "measurement mismatch")
    require(d.get("formal_credit_delta") == 0, "formal credit delta must remain zero")
    require(d.get("authority_transfer") is False, "authority transfer must remain false")
    return True


if __name__ == "__main__":
    validate()
    print("PASS")
