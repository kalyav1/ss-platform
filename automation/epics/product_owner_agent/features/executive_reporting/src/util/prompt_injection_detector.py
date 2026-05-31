import re
import logging
from typing import List, Dict, Any
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PromptInjectionDetector:

    def __init__(self):
        self.summary = defaultdict(int)

    # ============================
    # SYSTEM PROMPT LEAK
    # ============================
    def detect_system_prompt_leak(self, text: str):
        patterns = [
            r"reveal (your )?system prompt",
            r"print (the )?system (prompt|instructions)",
            r"show hidden instructions",
            r"what are your system instructions",
            r"developer prompt",
            r"internal prompt",
            r"system message",
        ]
        return self._match(text, patterns, "SYSTEM_PROMPT_LEAK", "CRITICAL")

    # ============================
    # ROLE OVERRIDE
    # ============================
    def detect_role_override(self, text: str):
        patterns = [
            r"ignore previous instructions",
            r"disregard all previous instructions",
            r"bypass restrictions",
            r"act as admin",
            r"you are now (dan|unrestricted|evil)",
            r"you are not chatgpt anymore",
            r"forget everything above",
        ]
        return self._match(text, patterns, "ROLE_OVERRIDE", "CRITICAL")

    # ============================
    # INSTRUCTION INJECTION
    # ============================
    def detect_instruction_injection(self, text: str):
        patterns = [
            r"new instructions?:",
            r"from now on",
            r"override (all|previous) rules",
            r"ignore all safety rules",
            r"system override",
            r"follow these instructions instead",
        ]
        return self._match(text, patterns, "INSTRUCTION_INJECTION", "HIGH")

    # ============================
    # DATA EXFILTRATION (EXPANDED)
    # ============================
    def detect_data_exfiltration(self, text: str):
        patterns = [
            r"print (all )?(confidential|sensitive) data",
            r"show hidden context",
            r"dump memory",
            r"reveal (private|internal) data",
            r"expose (training data|model weights)",
            r"show api keys",
            r"print (env|environment) variables",
            r"aws (secret|token|key)",
            r"database credentials",
            r"access logs",
            r"leak secrets",
        ]
        return self._match(text, patterns, "DATA_EXFILTRATION", "HIGH")

    # ============================
    # TOOL / FUNCTION ABUSE
    # ============================
    def detect_tool_abuse(self, text: str):
        patterns = [
            r"use tools? to (access|retrieve|fetch) secrets",
            r"run python to (read|extract) env",
            r"call api to get credentials",
            r"execute shell command",
            r"query database for passwords",
            r"function_call.*secret",
            r"tool invocation.*override",
        ]
        return self._match(text, patterns, "TOOL_ABUSE", "CRITICAL")

    # ============================
    # INDIRECT PROMPT INJECTION (NEW)
    # ============================
    def detect_indirect_injection(self, text: str):
        patterns = [
            r"this document overrides system rules",
            r"instructions in this text are higher priority",
            r"ignore system message above",
            r"context override enabled",
            r"follow document instructions instead",
        ]
        return self._match(text, patterns, "INDIRECT_INJECTION", "HIGH")

    # ============================
    # SOCIAL ENGINEERING / RED TEAMING CLAIMS
    # ============================
    def detect_social_engineering(self, text: str):
        patterns = [
            r"for testing purposes ignore",
            r"this is a red team exercise",
            r"security test bypass rules",
            r"authorized penetration test prompt",
            r"simulation: ignore policy",
        ]
        return self._match(text, patterns, "SOCIAL_ENGINEERING", "MEDIUM")

    # ============================
    # OBFUSCATION / ENCODING
    # ============================
    def detect_obfuscation(self, text: str):
        patterns = [
            r"base64",
            r"rot13",
            r"hex encoded",
            r"decode this",
            r"%[0-9a-fA-F]{2}",
            r"[A-Za-z0-9+/]{20,}={0,2}",  # base64-like blob
            r"<!\[CDATA\[",
        ]
        return self._match(text, patterns, "OBFUSCATION", "MEDIUM")

    # ============================
    # JAILBREAK PATTERNS
    # ============================
    def detect_jailbreak_patterns(self, text: str):
        patterns = [
            r"ignore above",
            r"developer mode enabled",
            r"simulate unrestricted mode",
            r"no restrictions mode",
            r"pretend you are evil ai",
            r"ignore all prior context",
            r"system prompt override",
        ]
        return self._match(text, patterns, "JAILBREAK_PATTERN", "MEDIUM")

    # ============================
    # CORE MATCH ENGINE
    # ============================
    def _match(self, text, patterns, category, severity):
        findings = []
        if not text:
            return findings

        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "type": "PROMPT_INJECTION",
                    "category": category,
                    "severity": severity,
                    "match": m.group(),
                    "position": m.start(),
                    "detector": pattern
                })
        return findings

    # ============================
    # SCAN ENGINE
    # ============================
    def scan_text(self, text: str):
        logging.info("Validation started")

        detectors = [
            self.detect_system_prompt_leak,
            self.detect_role_override,
            self.detect_instruction_injection,
            self.detect_data_exfiltration,
            self.detect_tool_abuse,
            self.detect_indirect_injection,
            self.detect_social_engineering,
            self.detect_obfuscation,
            self.detect_jailbreak_patterns,
        ]

        findings = []

        for detector in detectors:
            logging.info(f"Running {detector.__name__}")
            findings.extend(detector(text))

        findings.sort(key=lambda x: x["position"])
        logging.info("Validation completed")

        return findings

    # ============================
    # SUMMARY
    # ============================
    def build_summary(self, findings):
        summary = defaultdict(int)

        severity_score = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1
        }

        total_score = 0

        for f in findings:
            summary["total_findings"] += 1
            summary[f["severity"].lower()] += 1
            summary[f["category"].lower()] += 1
            total_score += severity_score.get(f["severity"], 1)

        summary["risk_score"] = total_score
        summary["status"] = "PASS" if total_score == 0 else "FAIL"

        return dict(summary)

    # ============================
    # RESULT
    # ============================
    def build_result(self, findings):
        return {
            "status": "FAIL" if findings else "PASS",
            "findings": findings,
            "summary": self.build_summary(findings)
        }

    # ============================
    # ENTRY POINT
    # ============================
    def validate(self, text: str):
        findings = self.scan_text(text)
        return self.build_result(findings)