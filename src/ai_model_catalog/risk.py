from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

# conservative buckets for LGPL-2.1 distribution context
CLEAR_PERMISSIVE = {"mit", "bsd-2-clause", "bsd-3-clause", "isc", "unlicense"}
CLEARLY_INCOMPATIBLE = {
    "gpl-2.0-only",
    "gpl-3.0-only",
    "agpl-3.0-only",
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
}
REVIEW_NEEDED = {
    "apache-2.0",
    "lgpl-2.1-only",
    "lgpl-2.1-or-later",
    "lgpl-3.0-only",
    "lgpl-3.0-or-later",
    "mpl-2.0",
}


@dataclass
class RiskInput:
    license_id: Optional[str]
    has_readme: bool
    has_license_section: bool
    has_training_data_info: bool
    has_eval_info: bool
    maintainer_active: Optional[bool] = None
    deserialization_uses_pickle: Optional[bool] = None
    has_model_card: Optional[bool] = None


@dataclass
class RiskFinding:
    severity: str  # "info" | "warn" | "high"
    message: str


@dataclass
class RiskReport:
    license_status: str  # "compatible" | "incompatible" | "needs-legal-review" | "unknown"
    findings: List[RiskFinding]


def _norm(s: Optional[str]) -> Optional[str]:
    return (s or "").strip().lower() or None


def license_compatibility_with_lgpl21(license_id: Optional[str]) -> str:
    lid = _norm(license_id)
    if not lid:
        return "unknown"
    if lid in CLEAR_PERMISSIVE:
        return "compatible"
    if lid in CLEARLY_INCOMPATIBLE:
        return "incompatible"
    if lid in REVIEW_NEEDED:
        return "needs-legal-review"
    return "needs-legal-review"


def assess_risks(inp: RiskInput) -> RiskReport:
    findings: List[RiskFinding] = []
    status = license_compatibility_with_lgpl21(inp.license_id)

    if status == "incompatible":
        findings.append(
            RiskFinding("high", "License incompatible with LGPL-2.1; distribution not allowed.")
        )
    elif status == "needs-legal-review":
        findings.append(
            RiskFinding("warn", "License requires legal review for LGPL-2.1 distribution.")
        )
    elif status == "unknown":
        findings.append(
            RiskFinding("warn", "No SPDX license detected; add a LICENSE and mention in README.")
        )

    if not inp.has_readme:
        findings.append(RiskFinding("high", "No README — reuse ramp-up & provenance risk."))
    if not inp.has_license_section:
        findings.append(
            RiskFinding("high", "README missing 'License' section — unclear provenance/terms.")
        )
    if not inp.has_training_data_info:
        findings.append(RiskFinding("warn", "No training data/dataset provenance documented."))
    if not inp.has_eval_info:
        findings.append(RiskFinding("warn", "No evaluation/benchmark details documented."))
    if inp.maintainer_active is False:
        findings.append(RiskFinding("warn", "Maintainers appear inactive recently — support risk."))
    if inp.deserialization_uses_pickle:
        findings.append(
            RiskFinding("high", "Untrusted pickle deserialization — remote code execution risk.")
        )
    if inp.has_model_card is False:
        findings.append(RiskFinding("warn", "No model card — missing intended use/risk guidance."))

    return RiskReport(license_status=status, findings=findings)
