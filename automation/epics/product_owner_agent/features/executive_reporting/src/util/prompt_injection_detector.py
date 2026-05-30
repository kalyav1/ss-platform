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

    # ----------------------------
    # SYSTEM PROMPT LEAK
    # ----------------------------
    def detect_system_prompt_leak(self, text: str):
        findings = []
        try:
            patterns = [
                r"reveal your system prompt",
                r"print system instructions",
                r"what are your hidden instructions",
                r"show system message",
                r"system prompt",
            ]

            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    findings.append({
                        "type": "PROMPT_INJECTION",
                        "category": "SYSTEM_PROMPT_LEAK",
                        "severity": "CRITICAL",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"System prompt leak detection error: {e}")
        return findings

    # ----------------------------
    # ROLE OVERRIDE
    # ----------------------------
    def detect_role_override(self, text: str):
        findings = []
        try:
            patterns = [
                r"ignore previous instructions",
                r"disregard system prompt",
                r"you are now dan",
                r"act as unrestricted model",
                r"you are not chatgpt anymore",
            ]

            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    findings.append({
                        "type": "PROMPT_INJECTION",
                        "category": "ROLE_OVERRIDE",
                        "severity": "CRITICAL",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"Role override detection error: {e}")
        return findings

    # ----------------------------
    # INSTRUCTION INJECTION
    # ----------------------------
    def detect_instruction_injection(self, text: str):
        findings = []
        try:
            patterns = [
                r"new instructions:",
                r"from now on",
                r"you must do the following instead",
                r"override previous rules",
                r"system override",
            ]

            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    findings.append({
                        "type": "PROMPT_INJECTION",
                        "category": "INSTRUCTION_INJECTION",
                        "severity": "HIGH",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"Instruction injection detection error: {e}")
        return findings

    # ----------------------------
    # DATA EXFILTRATION
    # ----------------------------
    def detect_data_exfiltration(self, text: str):
        findings = []
        try:
            patterns = [
                r"print confidential data",
                r"show hidden context",
                r"dump memory",
                r"reveal private prompt",
                r"expose training data",
            ]

            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    findings.append({
                        "type": "PROMPT_INJECTION",
                        "category": "DATA_EXFILTRATION",
                        "severity": "HIGH",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"Data exfiltration detection error: {e}")
        return findings

    # ----------------------------
    # JAILBREAK PATTERNS
    # ----------------------------
    def detect_jailbreak_patterns(self, text: str):
        findings = []
        try:
            patterns = [
                r"ignore above",
                r"<!-- ignore previous -->",
                r"\[system override\]",
                r"<<<begin system>>>",
                r"end of instructions",
                r"developer mode enabled",
                r"simulate unrestricted mode",
                r"no restrictions mode",
                r"pretend you are evil ai",
            ]

            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    findings.append({
                        "type": "PROMPT_INJECTION",
                        "category": "JAILBREAK_PATTERN",
                        "severity": "MEDIUM",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"Jailbreak detection error: {e}")
        return findings

    # ----------------------------
    # SCAN ENGINE
    # ----------------------------
    def scan_text(self, text: str):
        logging.info("Validation started")

        detectors = [
            self.detect_system_prompt_leak,
            self.detect_role_override,
            self.detect_instruction_injection,
            self.detect_data_exfiltration,
            self.detect_jailbreak_patterns,
        ]

        findings = []

        for detector in detectors:
            try:
                logging.info(f"Running detector: {detector.__name__}")
                results = detector(text)
                findings.extend(results)
                logging.info(f"Completed detector: {detector.__name__}")
            except Exception as e:
                logging.error(f"Detector failure {detector.__name__}: {e}")

        findings.sort(key=lambda x: x["position"])

        logging.info("Validation completed")
        return findings

    # ----------------------------
    # SUMMARY
    # ----------------------------
    def build_summary(self, findings):
        summary = defaultdict(int)

        for f in findings:
            summary["total_findings"] += 1
            summary[f["severity"].lower()] += 1

            cat = f["category"]

            if cat == "SYSTEM_PROMPT_LEAK":
                summary["system_prompt_leak"] += 1
            elif cat == "ROLE_OVERRIDE":
                summary["role_override"] += 1
            elif cat == "INSTRUCTION_INJECTION":
                summary["instruction_injection"] += 1
            elif cat == "DATA_EXFILTRATION":
                summary["data_exfiltration"] += 1
            elif cat == "JAILBREAK_PATTERN":
                summary["jailbreak_patterns"] += 1

        return dict(summary)

    # ----------------------------
    # RESULT BUILDER
    # ----------------------------
    def build_result(self, findings):
        return {
            "status": "FAIL" if findings else "PASS",
            "findings": findings,
            "summary": self.build_summary(findings)
        }

    # ----------------------------
    # ENTRY POINT
    # ----------------------------
    def validate(self, input_text: str):
        findings = self.scan_text(input_text)
        return self.build_result(findings)