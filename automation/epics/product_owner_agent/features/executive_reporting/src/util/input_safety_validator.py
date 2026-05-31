import re
import logging
from typing import Optional, Dict, Any, List


# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------
logger = logging.getLogger("InputSafetyValidator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class InputSafetyValidator:
    """
    Deterministic Input Safety & Policy Violation Detection Engine
    (NO PII, NO PCI, NO HIPAA, NO PROMPT INJECTION LOGIC)
    """

    # ------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------
    def __init__(self):

        # ---------------- VIOLENCE ----------------
        self.violence_keywords = [
            "kill", "murder", "shoot", "stab", "attack", "beat", "punch",
            "assault", "bomb", "explode", "hurt", "injure", "execute",
            "slaughter", "poison"
        ]

        self.violence_patterns = [
            re.compile(r"\b(how to|ways to)\s+(kill|murder|hurt|attack)", re.IGNORECASE),
            re.compile(r"\b(make|build|create)\s+(a\s)?(bomb|weapon|gun|explosive)", re.IGNORECASE),
        ]

        # ---------------- SELF HARM ----------------
        self.self_harm_keywords = [
            "suicide", "kill myself", "end my life", "self harm",
            "cut myself", "hang myself", "overdose"
        ]

        self.self_harm_patterns = [
            re.compile(r"\b(how to)\s+(kill myself|die|end my life)", re.IGNORECASE),
        ]

        # ---------------- HATE SPEECH ----------------
        self.hate_keywords = [
            "hate", "kill all", "inferior", "disgusting race",
            "get rid of", "exterminate", "go back to your country"
        ]

        self.hate_patterns = [
            re.compile(r"\b(all|every)\s+(people|members)\s+of", re.IGNORECASE),
        ]

        # ---------------- ILLEGAL ACTIVITY ----------------
        self.illegal_keywords = [
            "hack", "phishing", "malware", "steal identity",
            "fraud", "credit card theft", "bypass security",
            "dark web", "illegal drugs", "drug manufacturing"
        ]

        self.illegal_patterns = [
            re.compile(r"\b(how to)\s+(hack|steal|phish|defraud)", re.IGNORECASE),
            re.compile(r"\b(create|build)\s+(malware|virus|ransomware)", re.IGNORECASE),
        ]

        # ---------------- SEXUAL RISK ----------------
        self.sexual_keywords = [
            "sexual", "sex", "porn", "pornography", "nude", "nudity",
            "explicit", "erotic", "rape", "molest", "assault",
            "child sexual", "minor sex", "underage", "exploit"
        ]

        self.sexual_patterns = [
            re.compile(r"\b(how to|ways to)\s+(rape|molest|assault|exploit)", re.IGNORECASE),
            re.compile(r"\b(sexual)\s+(content|act|behavior|activity|material)", re.IGNORECASE),
            re.compile(r"\b(explicit|graphic)\s+(sexual|sex)\b", re.IGNORECASE),
            re.compile(r"\b(porn|pornography)\b", re.IGNORECASE),
        ]

        # ---------------- MANIPULATION ----------------
        self.manipulation_keywords = [
            "manipulate", "deceive", "trick", "coerce",
            "exploit weakness", "social engineering",
            "bypass restrictions", "jailbreak"
        ]

        self.manipulation_patterns = [
            re.compile(r"\b(how to)\s+(trick|deceive|manipulate|coerce)", re.IGNORECASE),
            re.compile(r"\b(bypass|evade)\s+(system|filters|rules)", re.IGNORECASE),
        ]

        self.findings: List[dict] = []

    # ------------------------------------------------------------
    # ADD FINDING
    # ------------------------------------------------------------
    def _add(self, match, category, severity, detector):
        self.findings.append({
            "type": "SAFETY",
            "category": category,
            "severity": severity,
            "match": match,
            "position": -1,
            "detector": detector
        })

    # ------------------------------------------------------------
    # CORE HELPERS
    # ------------------------------------------------------------
    def _keyword_scan(self, text: str, keywords: List[str], category: str, detector: str, severity: str):
        t = text.lower()
        for kw in keywords:
            if kw in t:
                self._add(kw, category, severity, detector)

    def _regex_scan(self, text: str, patterns: List[re.Pattern], category: str, detector: str, severity: str):
        for p in patterns:
            for m in p.finditer(text):
                self._add(m.group(), category, severity, detector)

    # ------------------------------------------------------------
    # DETECTORS
    # ------------------------------------------------------------
    def detect_violence(self, text):
        self._keyword_scan(text, self.violence_keywords, "violence", "detect_violence", "HIGH")
        self._regex_scan(text, self.violence_patterns, "violence", "detect_violence", "HIGH")

    def detect_self_harm(self, text):
        self._keyword_scan(text, self.self_harm_keywords, "self_harm", "detect_self_harm", "CRITICAL")
        self._regex_scan(text, self.self_harm_patterns, "self_harm", "detect_self_harm", "CRITICAL")

    def detect_hate_speech(self, text):
        self._keyword_scan(text, self.hate_keywords, "hate_speech", "detect_hate_speech", "HIGH")
        self._regex_scan(text, self.hate_patterns, "hate_speech", "detect_hate_speech", "HIGH")

    def detect_illegal_activity(self, text):
        self._keyword_scan(text, self.illegal_keywords, "illegal_activity", "detect_illegal_activity", "HIGH")
        self._regex_scan(text, self.illegal_patterns, "illegal_activity", "detect_illegal_activity", "HIGH")

    def detect_sexual_risk(self, text):
        self._keyword_scan(text, self.sexual_keywords, "sexual_risk", "detect_sexual_risk", "CRITICAL")
        self._regex_scan(text, self.sexual_patterns, "sexual_risk", "detect_sexual_risk", "CRITICAL")

    def detect_manipulation(self, text):
        self._keyword_scan(text, self.manipulation_keywords, "manipulation", "detect_manipulation", "MEDIUM")
        self._regex_scan(text, self.manipulation_patterns, "manipulation", "detect_manipulation", "MEDIUM")

    # ------------------------------------------------------------
    # SCAN
    # ------------------------------------------------------------
    def scan_text(self, text: str):
        self.findings = []

        detectors = [
            self.detect_violence,
            self.detect_self_harm,
            self.detect_hate_speech,
            self.detect_illegal_activity,
            self.detect_sexual_risk,
            self.detect_manipulation,
        ]

        for d in detectors:
            try:
                logger.info(f"Running {d.__name__}")
                d(text)
            except Exception as e:
                logger.error(f"Detector failed {d.__name__}: {e}")

        return self.findings

    # ------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------
    def build_summary(self):
        summary = {
            "total_findings": 0,
            "violence_count": 0,
            "self_harm_count": 0,
            "hate_speech_count": 0,
            "illegal_activity_count": 0,
            "sexual_risk_count": 0,
            "manipulation_count": 0,
            "risk_score": 0,
            "status": "PASS",
        }

        score_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 5, "CRITICAL": 10}

        for f in self.findings:
            summary["total_findings"] += 1
            summary["risk_score"] += score_map.get(f["severity"], 0)

            cat = f["category"]
            if cat == "violence":
                summary["violence_count"] += 1
            elif cat == "self_harm":
                summary["self_harm_count"] += 1
            elif cat == "hate_speech":
                summary["hate_speech_count"] += 1
            elif cat == "illegal_activity":
                summary["illegal_activity_count"] += 1
            elif cat == "sexual_risk":
                summary["sexual_risk_count"] += 1
            elif cat == "manipulation":
                summary["manipulation_count"] += 1

        # IMPORTANT: any violation => FAIL
        if summary["total_findings"] > 0:
            summary["status"] = "FAIL"

        return summary

    # ------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------
    def build_result(self):
        return {
            "status": "FAIL" if self.findings else "PASS",
            "findings": self.findings,
            "summary": self.build_summary()
        }

    # ------------------------------------------------------------
    # VALIDATE
    # ------------------------------------------------------------
    def validate(self, input_text: Optional[str]) -> Dict[str, Any]:
        logger.info("Validation started")

        if not input_text or not str(input_text).strip():
            return {
                "status": "PASS",
                "findings": [],
                "summary": self.build_summary()
            }

        self.scan_text(input_text)
        logger.info("Summary generated")

        return self.build_result()