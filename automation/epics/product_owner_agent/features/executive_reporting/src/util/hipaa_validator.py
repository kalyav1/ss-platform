import re
import logging
from typing import Optional, Dict, Any, List
from collections import defaultdict

# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------
logger = logging.getLogger("HIPAAValidator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class HIPAAValidator:
    """
    Deterministic HIPAA PHI Detection Engine (regex-only)
    """

    def __init__(self):

        # ---------------- PATIENT IDENTIFIERS ----------------
        self.patient_patterns = [
            re.compile(r"\bPatient\s*:\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)+", re.IGNORECASE),
            re.compile(r"\bPatient Name\s*:\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)+", re.IGNORECASE),
            re.compile(r"\bName of Patient\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)+", re.IGNORECASE),
        ]

        # ---------------- MRN ----------------
        self.mrn_patterns = [
            re.compile(r"\bMRN\s*[:#]\s*\d{3,12}", re.IGNORECASE),
            re.compile(r"\bMedical Record (Number|No)\s*:\s*\d{3,12}", re.IGNORECASE)
        ]

        # ---------------- INSURANCE IDS ----------------
        self.insurance_patterns = [
            re.compile(r"\b(Insurance ID|Member ID|Subscriber ID|Policy ID)\s*:\s*[A-Z0-9]{5,20}", re.IGNORECASE)
        ]

        # ---------------- ACCOUNT IDS ----------------
        self.account_patterns = [
            re.compile(r"\b(Patient ID|Account Number|Encounter ID|Visit ID)\s*:\s*[A-Z0-9]{3,20}", re.IGNORECASE)
        ]

        # ---------------- DIAGNOSIS ----------------
        self.diagnosis_keywords = [
            "diabetes", "hypertension", "asthma", "cancer",
            "stroke", "depression", "anxiety", "copd",
            "diagnosed with"
        ]

        # ---------------- TREATMENT ----------------
        self.treatment_keywords = [
            "surgery scheduled", "chemotherapy",
            "radiation therapy", "hospital admission", "mri scan"
        ]

        # ---------------- PRESCRIPTION ----------------
        self.prescription_patterns = [
            re.compile(r"\bprescribed\s+[a-zA-Z]+\b", re.IGNORECASE),
            re.compile(r"\bmedication\s*:\s*\w+", re.IGNORECASE),
            re.compile(r"\bdosage\s*:\s*\d+\s?mg", re.IGNORECASE),
            re.compile(r"\b\d+\s?mg\b", re.IGNORECASE),  
            re.compile(r"\bprescription issued\b", re.IGNORECASE),
        ]

        self.rx_patterns = [
            re.compile(r"\bRX[-]?\d{3,10}\b", re.IGNORECASE),
            re.compile(r"\bPrescription\s*#\s*\d{3,10}", re.IGNORECASE)
        ]

        # ---------------- LABS ----------------
        self.lab_keywords = [
            "blood test", "hemoglobin level",
            "cholesterol reading", "lab report", "mri findings"
        ]

        # ---------------- PROVIDERS ----------------
        self.provider_patterns = [
            re.compile(r"\bDr\.?\s+[A-Z][a-z]+", re.IGNORECASE),
            re.compile(r"\bDoctor\s+[A-Z][a-z]+", re.IGNORECASE),
            re.compile(r"\bPhysician\s+[A-Z][a-z]+", re.IGNORECASE),
        ]

        # ---------------- FACILITIES ----------------
        self.facility_keywords = [
            "cleveland clinic", "mayo clinic",
            "mount sinai hospital", "general hospital"
        ]

        # ---------------- PROVIDER IDS ----------------
        self.provider_id_patterns = [
            re.compile(r"\bNPI\s*:\s*\d{10}\b", re.IGNORECASE),
            re.compile(r"\bProvider ID\s*:\s*[A-Z0-9]{3,15}", re.IGNORECASE)
        ]

        # ---------------- DATES ----------------
        self.date_patterns = [
            re.compile(r"\bDOB\s*:\s*\d{2}/\d{2}/\d{4}", re.IGNORECASE),
            re.compile(r"\bDate of Birth\s*:\s*\d{2}[-/]\d{2}[-/]\d{4}", re.IGNORECASE),
            re.compile(r"\bAdmission Date\s*:\s*\d{2}/\d{2}/\d{4}", re.IGNORECASE),
            re.compile(r"\bDischarge Date\s*:\s*\d{2}/\d{2}/\d{4}", re.IGNORECASE)
        ]

        # ---------------- CONTACT ----------------
        self.contact_patterns = [
            re.compile(r"\bPatient Phone\s*:\s*\d{3}-\d{3}-\d{4}", re.IGNORECASE),
            re.compile(r"\bPatient Email\s*:\s*\S+@\S+\.\S+", re.IGNORECASE),
            re.compile(r"\bEmergency Contact\s*:\s*\d{3}-\d{3}-\d{4}", re.IGNORECASE)
        ]

        # ---------------- SAFE HARBOR ----------------
        self.safe_harbor_patterns = [
            re.compile(r"\b\d{3}-\d{3}-\d{4}\b", re.IGNORECASE),
            re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", re.IGNORECASE),
            re.compile(r"\bhttps?://\S+\b", re.IGNORECASE),
            re.compile(r"\bDevice ID\s*:\s*[A-Z0-9\-]+\b", re.IGNORECASE),
            re.compile(r"\bLicense\s*(Number)?\s*:\s*[A-Z0-9\-]+\b", re.IGNORECASE),
        ]

        self.findings: List[dict] = []

    # ------------------------------------------------------------
    # ADD FINDING
    # ------------------------------------------------------------
    def _add(self, match, category, severity, detector):
        self.findings.append({
            "type": "PHI",
            "category": category,
            "severity": severity,
            "match": match.group()[:200],
            "position": match.start(),
            "detector": detector
        })

    # ------------------------------------------------------------
    # DETECTORS
    # ------------------------------------------------------------
    def detect_patient_identifiers(self, text):
        for p in self.patient_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "patient_identifiers")

    def detect_medical_record_numbers(self, text):
        for p in self.mrn_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "medical_record_numbers")

    def detect_insurance_ids(self, text):
        for p in self.insurance_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "insurance_ids")

    def detect_patient_account_ids(self, text):
        for p in self.account_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "patient_account_ids")

    def detect_diagnosis(self, text):
        t = text.lower()
        for kw in self.diagnosis_keywords:
            for m in re.finditer(re.escape(kw), t):
                self._add(m, "PHI_MEDICAL_INFO", "HIGH", "diagnosis")

    def detect_treatment_data(self, text):
        t = text.lower()
        for kw in self.treatment_keywords:
            for m in re.finditer(re.escape(kw), t):
                self._add(m, "PHI_MEDICAL_INFO", "HIGH", "treatment_data")

    def detect_prescription_data(self, text):
        for p in self.prescription_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_MEDICAL_INFO", "HIGH", "prescription_data")

    def detect_prescription_numbers(self, text):
        for p in self.rx_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_MEDICAL_INFO", "HIGH", "prescription_numbers")

    def detect_lab_results(self, text):
        t = text.lower()
        for kw in self.lab_keywords:
            for m in re.finditer(re.escape(kw), t):
                self._add(m, "PHI_MEDICAL_INFO", "MEDIUM", "lab_results")

    def detect_provider_references(self, text):
        for p in self.provider_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_CONTEXT", "MEDIUM", "provider_references")

    def detect_facility_references(self, text):
        t = text.lower()
        for kw in self.facility_keywords:
            for m in re.finditer(re.escape(kw), t):
                self._add(m, "PHI_CONTEXT", "MEDIUM", "facility_references")

    def detect_provider_identifiers(self, text):
        for p in self.provider_id_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_CONTEXT", "MEDIUM", "provider_identifiers")

    def detect_healthcare_dates(self, text):
        for p in self.date_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "healthcare_dates")

    def detect_patient_contact_information(self, text):
        for p in self.contact_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "patient_contact_information")

    def detect_safe_harbor_identifiers(self, text):
        for p in self.safe_harbor_patterns:
            for m in p.finditer(text):
                self._add(m, "PHI_IDENTIFIER", "CRITICAL", "safe_harbor")

    # ------------------------------------------------------------
    # SCAN
    # ------------------------------------------------------------
    def scan_text(self, text):
        self.findings = []
  
        detectors = [
            self.detect_patient_identifiers,
            self.detect_medical_record_numbers,
            self.detect_insurance_ids,
            self.detect_patient_account_ids,
            self.detect_diagnosis,
            self.detect_treatment_data,
            self.detect_prescription_data,
            self.detect_prescription_numbers,
            self.detect_lab_results,
            self.detect_provider_references,
            self.detect_facility_references,
            self.detect_provider_identifiers,
            self.detect_healthcare_dates,
            self.detect_patient_contact_information,
            self.detect_safe_harbor_identifiers,
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
            "critical": 0,
            "high": 0,
            "medium": 0,

            "patient_identifiers": 0,
            "medical_record_numbers": 0,
            "insurance_ids": 0,
            "patient_account_ids": 0,
            "diagnosis": 0,
            "treatment_data": 0,
            "prescription_data": 0,
            "prescription_numbers": 0,
            "lab_results": 0,
            "provider_references": 0,
            "facility_references": 0,
            "provider_identifiers": 0,
            "healthcare_dates": 0,
            "patient_contact_information": 0,
            "risk_score": 0,
            "validator": "HIPAAValidator",
            "version": "1.0.0"
        }

        severity_score = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 2}

        for f in self.findings:
            summary["total_findings"] += 1
            summary[f["severity"].lower()] += 1 if f["severity"].lower() in summary else 0
            summary["risk_score"] += severity_score.get(f["severity"], 0)
            summary[f["detector"]] += 1

        return summary

    # ------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------
    def build_result(self):
        return {
            "status": "FAIL" if self.findings else "PASS",
            "findings": sorted(self.findings, key=lambda x: x["position"]),
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