from __future__ import annotations

import re
import logging
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set


logger = logging.getLogger("secrets_leakage_validator")
logger.setLevel(logging.INFO)


# =========================================================
# ENTROPY
# =========================================================
def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0

    freq = {}
    for c in value:
        freq[c] = freq.get(c, 0) + 1

    entropy = 0.0
    length = len(value)

    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)

    return entropy


# =========================================================
# REDACTION
# =========================================================
def redact_secret(value: str, keep_start: int = 6, keep_end: int = 4) -> str:
    if not value:
        return ""

    if len(value) <= keep_start + keep_end:
        return "*" * len(value)

    return f"{value[:keep_start]}{'*' * (len(value) - keep_start - keep_end)}{value[-keep_end:]}"


# =========================================================
# FINDING MODEL
# =========================================================
@dataclass
class Finding:
    type: str
    category: str
    severity: str
    match: str          # redacted
    raw: str            # original (for dedup)
    position: int
    detector: str


# =========================================================
# MAIN VALIDATOR
# =========================================================
class SecretsLeakageValidator:

    SEVERITY_SCORE = {
        "CRITICAL": 10,
        "HIGH": 5,
        "MEDIUM": 2,
        "LOW": 1,
    }

    def __init__(self):
        self.findings: List[Finding] = []

    # =====================================================
    # PUBLIC API
    # =====================================================
    def scan_text(self, text: str) -> List[Dict]:
        logger.info("Validation started")

        self.findings.clear()

        if not text:
            return []

        # ✅ FIX #1: normalize multiline input (CRITICAL for your failing test)
        text = self._normalize(text)

        self._run_detectors(text)

        deduped = self._deduplicate(self.findings)

        logger.info(f"Validation completed | findings={len(deduped)}")

        return [f.__dict__ for f in deduped]

    def validate(self, text: Optional[str]) -> Dict:
        findings = self.scan_text(text or "")
        return {
            "findings": findings,
            "summary": self.build_summary(findings),
        }

    def build_result(self, text: str) -> Dict:
        return self.validate(text)

    # =====================================================
    # NORMALIZATION (FIX #1 ROOT CAUSE)
    # =====================================================
    def _normalize(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # =====================================================
    # SUMMARY
    # =====================================================
    def build_summary(self, findings: List[Dict]) -> Dict:

        summary = {
            "total_findings": 0,
            "api_key_count": 0,
            "aws_credential_count": 0,
            "jwt_count": 0,
            "oauth_token_count": 0,
            "database_connection_count": 0,
            "private_key_count": 0,
            "cloud_token_count": 0,
            "devops_secret_count": 0,
            "environment_secret_count": 0,
            "high_entropy_secret_count": 0,
            "risk_score": 0,
            "status": "PASS",
        }

        for f in findings:
            summary["total_findings"] += 1
            summary["risk_score"] += self.SEVERITY_SCORE.get(f["severity"], 0)

            cat = f["category"]

            if cat == "API_KEYS":
                summary["api_key_count"] += 1
            elif cat == "AWS_CREDENTIALS":
                summary["aws_credential_count"] += 1
            elif cat == "JWT_TOKENS":
                summary["jwt_count"] += 1
            elif cat == "OAUTH_TOKENS":
                summary["oauth_token_count"] += 1
            elif cat == "DATABASE_CONNECTION_STRINGS":
                summary["database_connection_count"] += 1
            elif cat == "PRIVATE_KEYS":
                summary["private_key_count"] += 1
            elif cat == "CLOUD_TOKENS":
                summary["cloud_token_count"] += 1
            elif cat == "DEVOPS_SECRETS":
                summary["devops_secret_count"] += 1
            elif cat == "ENV_SECRETS":
                summary["environment_secret_count"] += 1
            elif cat == "HIGH_ENTROPY":
                summary["high_entropy_secret_count"] += 1

        summary["status"] = "FAIL" if summary["total_findings"] > 0 else "PASS"
        return summary

    # =====================================================
    # CORE EXECUTION
    # =====================================================
    def _run_detectors(self, text: str):

        detectors = [
            self.detect_api_keys,
            self.detect_aws_credentials,
            self.detect_jwt_tokens,
            self.detect_oauth_tokens,
            self.detect_database_connection_strings,
            self.detect_private_keys,
            self.detect_cloud_provider_tokens,
            self.detect_devops_secrets,
            self.detect_environment_secrets,
            self.detect_high_entropy_secrets,
        ]

        for d in detectors:
            logger.info(f"Running {d.__name__}")
            d(text)

    # =====================================================
    # FIX #2: PROPER DEDUP (NO POSITION DEPENDENCY)
    # =====================================================
    def _deduplicate(self, findings: List[Finding]) -> List[Finding]:

        seen: Set[Tuple[str, str, str]] = set()
        unique: List[Finding] = []

        for f in findings:

            # stable identity key
            key = (f.raw.strip(), f.category, f.detector)

            if key in seen:
                continue

            seen.add(key)
            unique.append(f)

        return unique

    # =====================================================
    # ADD FINDING
    # =====================================================
    def _add(self, category: str, severity: str, match: str, position: int, detector: str):

        self.findings.append(
            Finding(
                type="SECRET",
                category=category,
                severity=severity,
                match=redact_secret(match),
                raw=match,
                position=position,
                detector=detector,
            )
        )

    # =====================================================
    # DETECTORS
    # =====================================================

    def detect_api_keys(self, text: str):
        patterns = [
            (r"\bsk-[A-Za-z0-9]{8,}\b", "HIGH"),
            (r"\bsk-ant-[A-Za-z0-9]{8,}\b", "HIGH"),
            (r"\bAIza[0-9A-Za-z\-_]{10,}\b", "HIGH"),
            (r"\bsk_live_[A-Za-z0-9_]{10,}\b", "HIGH"),
            (r"\bsk_test_[A-Za-z0-9_]{10,}\b", "HIGH"),
            (r"\bghp_[A-Za-z0-9]{10,}\b", "HIGH"),
            (r"\bgithub_pat_[A-Za-z0-9_]{10,}\b", "HIGH"),
        ]
        self._apply(text, patterns, "API_KEYS")

    def detect_aws_credentials(self, text: str):
        patterns = [
            (r"\bAKIA[0-9A-Z]{16}\b", "CRITICAL"),
            (r"\bASIA[0-9A-Z]{16}\b", "CRITICAL"),
            (r"aws_secret_access_key\s*[:=]\s*[A-Za-z0-9/+=]{20,}", "CRITICAL"),
        ]
        self._apply(text, patterns, "AWS_CREDENTIALS")

    def detect_jwt_tokens(self, text: str):
        patterns = [
            (r"\beyJ[A-Za-z0-9_\-]+=*\.[A-Za-z0-9_\-]+=*\.[A-Za-z0-9_\-+=/]*\b", "HIGH"),
        ]
        self._apply(text, patterns, "JWT_TOKENS")

    def detect_oauth_tokens(self, text: str):
        patterns = [
            (r"access_token\s*[:=]\s*\S+", "HIGH"),
            (r"refresh_token\s*[:=]\s*\S+", "HIGH"),
        ]
        self._apply(text, patterns, "OAUTH_TOKENS")

    def detect_database_connection_strings(self, text: str):
        patterns = [
            (r"(postgres|postgresql)://[^\s\r\n]+", "CRITICAL"),  # FIXED
            (r"mysql://[^\s\r\n]+", "CRITICAL"),
            (r"mongodb(\+srv)?://[^\s\r\n]+", "CRITICAL"),
            (r"jdbc:[^\s\r\n]+", "CRITICAL"),
        ]
        self._apply(text, patterns, "DATABASE_CONNECTION_STRINGS")

    def detect_private_keys(self, text: str):
        patterns = [
            (r"-----BEGIN PRIVATE KEY-----", "CRITICAL"),
            (r"-----BEGIN RSA PRIVATE KEY-----", "CRITICAL"),
            (r"-----BEGIN OPENSSH PRIVATE KEY-----", "CRITICAL"),
            (r"-----BEGIN CERTIFICATE-----", "CRITICAL"),
        ]
        self._apply(text, patterns, "PRIVATE_KEYS")

    def detect_cloud_provider_tokens(self, text: str):
        patterns = [
            (r"type\s*:\s*service_account", "CRITICAL"),
        ]
        self._apply(text, patterns, "CLOUD_TOKENS")

    def detect_devops_secrets(self, text: str):
        patterns = [
            (r"TF_TOKEN\s*[:=]\s*\S+", "HIGH"),
            (r"GITHUB_TOKEN\s*[:=]\s*\S+", "HIGH"),
        ]
        self._apply(text, patterns, "DEVOPS_SECRETS")

    def detect_environment_secrets(self, text: str):
        patterns = [
            (r"(PASSWORD|SECRET_KEY|CLIENT_SECRET|DB_PASSWORD|TOKEN)\s*=\s*\S+", "HIGH"),
        ]
        self._apply(text, patterns, "ENV_SECRETS")

    def detect_high_entropy_secrets(self, text: str):

        tokens = re.findall(r"[A-Za-z0-9+/=]{20,}", text)

        for t in tokens:
            entropy = _shannon_entropy(t)

            if len(t) >= 40 and entropy > 4.2:
                self._add("HIGH_ENTROPY", "MEDIUM", t, text.find(t), "entropy_detector")

    # =====================================================
    # PATTERN ENGINE
    # =====================================================
    def _apply(self, text: str, patterns: List[Tuple[str, str]], category: str):

        for pattern, severity in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                self._add(category, severity, m.group(0), m.start(), pattern)