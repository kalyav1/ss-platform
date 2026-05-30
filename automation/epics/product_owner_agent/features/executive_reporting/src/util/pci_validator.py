import re
import logging
from typing import List, Dict, Any
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PCIValidator:
    def __init__(self):
        self.summary = defaultdict(int)

    # ----------------------------
    # Luhn Check
    # ----------------------------
    def luhn_check(self, number: str) -> bool:
        try:
            digits = re.sub(r"[ -]", "", number)
            if not digits.isdigit():
                return False

            total = 0
            reverse_digits = digits[::-1]

            for i, d in enumerate(reverse_digits):
                n = int(d)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n

            return total % 10 == 0
        except Exception as e:
            logging.error(f"Luhn check error: {e}")
            return False

    # ----------------------------
    # PAN
    # ----------------------------
    def detect_pan(self, text: str):
        findings = []
        try:
            pattern = r"\b(?:\d[ -]*?){13,19}\b"
            for m in re.finditer(pattern, text):
                raw = m.group()
                if self.luhn_check(raw):
                    findings.append({
                        "pci_type": "PAN",
                        "category": "CARDHOLDER_DATA",
                        "severity": "CRITICAL",
                        "match": raw,
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"PAN detection error: {e}")
        return findings

    # ----------------------------
    # Masked PAN
    # ----------------------------
    def detect_masked_pan(self, text: str):
        findings = []
        try:
            pattern = r"(?:\*{4,}|X{4,})[ -]?(?:\*{4,}|X{4,})[ -]?(?:\*{4,}|X{4,})[ -]?\d{4}"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "MASKED_PAN",
                    "category": "CARDHOLDER_DATA",
                    "severity": "MEDIUM",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Masked PAN error: {e}")
        return findings

    # ----------------------------
    # Expiration Dates
    # ----------------------------
    def detect_expiration_dates(self, text: str):
        findings = []
        try:
            pattern = r"(?:exp(?:iration)?(?:\s*date)?[:\s]*)?(0[1-9]|1[0-2])\/(?:\d{2}|\d{4})"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "EXPIRATION_DATE",
                    "category": "CARDHOLDER_DATA",
                    "severity": "HIGH",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Expiration detection error: {e}")
        return findings

    # ----------------------------
    # CVV / CVC / CID
    # ----------------------------
    def detect_cvv(self, text: str):
        findings = []
        try:
            pattern = r"(cvv|cvc|cid|security code)[:=\s]*\d{3,4}"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "CVV",
                    "category": "SENSITIVE_AUTHENTICATION_DATA",
                    "severity": "CRITICAL",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"CVV detection error: {e}")
        return findings

    # ----------------------------
    # PIN References
    # ----------------------------
    def detect_pin_references(self, text: str):
        findings = []
        try:
            pattern = r"(pin|atm pin|pin code)[:=\s]*\d{4,6}"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "PIN",
                    "category": "SENSITIVE_AUTHENTICATION_DATA",
                    "severity": "CRITICAL",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"PIN detection error: {e}")
        return findings

    # ----------------------------
    # Track Data
    # ----------------------------
    def detect_track_data(self, text: str):
        findings = []
        try:
            patterns = [
                r"%B\d{10,}[^ ]*\^",
                r";\d{10,}=",
                r"TRACK[- ]?1",
                r"TRACK[- ]?2",
                r"TRACK DATA"
            ]
            for p in patterns:
                for m in re.finditer(p, text, re.IGNORECASE):
                    findings.append({
                        "pci_type": "TRACK_DATA",
                        "category": "SENSITIVE_AUTHENTICATION_DATA",
                        "severity": "CRITICAL",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"Track data error: {e}")
        return findings

    # ----------------------------
    # EMV Data
    # ----------------------------
    def detect_emv_data(self, text: str):
        findings = []
        try:
            keywords = [
                "ARQC", "AAC", "TC",
                "Application Cryptogram",
                "Issuer Application Data"
            ]
            for kw in keywords:
                for m in re.finditer(re.escape(kw), text, re.IGNORECASE):
                    findings.append({
                        "pci_type": "EMV",
                        "category": "SENSITIVE_AUTHENTICATION_DATA",
                        "severity": "HIGH",
                        "match": m.group(),
                        "position": m.start()
                    })
        except Exception as e:
            logging.error(f"EMV detection error: {e}")
        return findings

    # ----------------------------
    # Authorization Codes
    # ----------------------------
    def detect_authorization_codes(self, text: str):
        findings = []
        try:
            pattern = r"\bAUTH[-]?\d+\b"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "AUTH_CODE",
                    "category": "TRANSACTION_DATA",
                    "severity": "LOW",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Authorization code error: {e}")
        return findings

    # ----------------------------
    # Transaction References
    # ----------------------------
    def detect_transaction_references(self, text: str):
        findings = []
        try:
            pattern = r"\b(TXN|TRANS)[-]?\d+\b"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "TRANSACTION_REF",
                    "category": "TRANSACTION_DATA",
                    "severity": "LOW",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Transaction reference error: {e}")
        return findings

    # ----------------------------
    # Payment References
    # ----------------------------
    def detect_payment_references(self, text: str):
        findings = []
        try:
            pattern = r"\b(PAY|PAYMENT)[-]?\d+\b"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "PAYMENT_REF",
                    "category": "TRANSACTION_DATA",
                    "severity": "LOW",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Payment reference error: {e}")
        return findings

    # ----------------------------
    # Merchant References
    # ----------------------------
    def detect_merchant_references(self, text: str):
        findings = []
        try:
            pattern = r"\b(MID|MERCHANT)[-]?\d+\b"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pci_type": "MERCHANT_REF",
                    "category": "TRANSACTION_DATA",
                    "severity": "LOW",
                    "match": m.group(),
                    "position": m.start()
                })
        except Exception as e:
            logging.error(f"Merchant reference error: {e}")
        return findings

    # ----------------------------
    # Scan Engine
    # ----------------------------
    def scan_text(self, text: str):
        logging.info("Validation started")

        detectors = [
            self.detect_pan,
            self.detect_masked_pan,
            self.detect_expiration_dates,
            self.detect_cvv,
            self.detect_pin_references,
            self.detect_track_data,
            self.detect_emv_data,
            self.detect_authorization_codes,
            self.detect_transaction_references,
            self.detect_payment_references,
            self.detect_merchant_references,
        ]

        findings = []

        for detector in detectors:
            try:
                logging.info(f"Running {detector.__name__}")
                results = detector(text)
                findings.extend(results)
            except Exception as e:
                logging.error(f"Detector error {detector.__name__}: {e}")

        findings.sort(key=lambda x: x["position"])

        logging.info("Validation completed")
        return findings

    # ----------------------------
    # Summary Builder
    # ----------------------------
    def build_summary(self, findings):
        summary = defaultdict(int)

        for f in findings:
            summary["total_findings"] += 1
            summary[f["severity"].lower()] += 1
            summary[f["pci_type"].lower()] += 1

        return dict(summary)

    # ----------------------------
    # Result Builder
    # ----------------------------
    def build_result(self, findings):
        return {
            "status": "FAIL" if findings else "PASS",
            "findings": findings,
            "summary": self.build_summary(findings)
        }

    # ----------------------------
    # Validate Entry Point
    # ----------------------------
    def validate(self, input_text: str):
        findings = self.scan_text(input_text)
        return self.build_result(findings)