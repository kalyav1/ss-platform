import re
import logging
import sys
from typing import List, Dict, Any


# ------------------------------------------------------------
# LOGGING CONFIGURATION
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ------------------------------------------------------------
# CORE DETECTOR CLASS
# ------------------------------------------------------------
class PIIVerifier:

    def __init__(self):
        self.detectors = [
            self.detect_emails,
            self.detect_phone_numbers,
            self.detect_ssn,
            self.detect_credit_cards,
            self.detect_ip_addresses,
            self.detect_passports,
            self.detect_driver_licenses,
            self.detect_employee_ids,
            self.detect_customer_ids,
            self.detect_account_numbers,
            self.detect_patient_ids,
            self.detect_medical_record_numbers,
            self.detect_dates_of_birth,
            self.detect_addresses,
            self.detect_zip_codes,
            self.detect_internal_user_ids,
            self.detect_device_ids,
            self.detect_ticket_ownership,
        ]

    # --------------------------------------------------------
    # UTIL
    # --------------------------------------------------------
    def add_finding(self, findings, pii_type, category, match, position):
        findings.append({
            "pii_type": pii_type,
            "category": category,
            "match": match,
            "position": position
        })

    # --------------------------------------------------------
    # DIRECT IDENTIFIERS
    # --------------------------------------------------------
    def detect_emails(self, text, findings):
        try:
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "EMAIL", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Email detector error: {e}")

    def detect_phone_numbers(self, text, findings):
        try:
            pattern = r'(\+?\d{1,2}[\s-]?)?(\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "PHONE", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Phone detector error: {e}")

    def detect_ssn(self, text, findings):
        try:
            pattern = r'\b\d{3}-\d{2}-\d{4}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "SSN", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"SSN detector error: {e}")

    def detect_credit_cards(self, text, findings):
        try:
            pattern = r'\b(?:\d[ -]*?){13,19}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "CREDIT_CARD", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Credit card detector error: {e}")

    def detect_ip_addresses(self, text, findings):
        try:
            pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "IP_ADDRESS", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"IP detector error: {e}")

    def detect_passports(self, text, findings):
        try:
            pattern = r'\b[A-PR-WYa-pr-wy][0-9]{8}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "PASSPORT", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Passport detector error: {e}")

    def detect_driver_licenses(self, text, findings):
        try:
            pattern = r'\bDL-?[A-Z0-9]{5,12}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "DRIVER_LICENSE", "DIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Driver license detector error: {e}")

    # --------------------------------------------------------
    # INDIRECT IDENTIFIERS
    # --------------------------------------------------------
    def detect_employee_ids(self, text, findings):
        try:
            pattern = r'\b(EMP-?\d{3,10}|E\d{5,10})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "EMPLOYEE_ID", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Employee ID detector error: {e}")

    def detect_customer_ids(self, text, findings):
        try:
            pattern = r'\b(CUST-?\d{3,10}|CUSTOMER-?\d{3,10})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "CUSTOMER_ID", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Customer ID detector error: {e}")

    def detect_account_numbers(self, text, findings):
        try:
            pattern = r'\b(ACCT-?\d{3,12}|ACCOUNT-?\d{3,12})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "ACCOUNT_NUMBER", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Account number detector error: {e}")

    def detect_patient_ids(self, text, findings):
        try:
            pattern = r'\b(PID-?\d{3,10}|PATIENT-?\d{3,10})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "PATIENT_ID", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Patient ID detector error: {e}")

    def detect_medical_record_numbers(self, text, findings):
        try:
            pattern = r'\bMRN-?\d{3,10}\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "MEDICAL_RECORD_NUMBER", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"MRN detector error: {e}")

    def detect_dates_of_birth(self, text, findings):
        try:
            patterns = [r'\b\d{2}/\d{2}/\d{4}\b', r'\b\d{4}-\d{2}-\d{2}\b']
            for pattern in patterns:
                for m in re.finditer(pattern, text):
                    self.add_finding(findings, "DATE_OF_BIRTH", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"DOB detector error: {e}")

    def detect_addresses(self, text, findings):
        try:
            pattern = r'\b\d{1,5}\s+[A-Z][a-zA-Z]+\s+(Street|St|Avenue|Ave|Road|Rd|Blvd|Lane|Drive)\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "ADDRESS", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Address detector error: {e}")

    def detect_zip_codes(self, text, findings):
        try:
            pattern = r'\b\d{5}(-\d{4})?\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "ZIP_CODE", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Zip detector error: {e}")

    def detect_internal_user_ids(self, text, findings):
        try:
            pattern = r'\b(user\d+|employee\d+|[a-z]{3,10}\d{1,4})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "INTERNAL_USER_ID", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Internal user ID detector error: {e}")

    def detect_device_ids(self, text, findings):
        try:
            pattern = r'\b(DEV-?\d{3,10}|HOST-?\d{3,10}|LAPTOP-?\d{3,10})\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "DEVICE_ID", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Device ID detector error: {e}")

    def detect_ticket_ownership(self, text, findings):
        try:
            pattern = r'\b(assigned_to|reporter|owner)=[a-zA-Z0-9.\-_]+\b'
            for m in re.finditer(pattern, text):
                self.add_finding(findings, "TICKET_OWNERSHIP", "INDIRECT", m.group(), m.start())
        except Exception as e:
            logging.error(f"Ticket ownership detector error: {e}")

    # --------------------------------------------------------
    # ENGINE
    # --------------------------------------------------------
    def scan(self, text: str) -> List[Dict[str, Any]]:
        findings = []

        logging.info("validation started")
        logging.info("detector execution started")

        for detector in self.detectors:
            detector(text, findings)

        logging.info(f"findings detected: {len(findings)}")
        return findings

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------
    def build_summary(self, findings):
        summary = {
            "total_findings": 0,
            "direct_identifiers": 0,
            "indirect_identifiers": 0
        }

        for f in findings:
            summary["total_findings"] += 1
            if f["category"] == "DIRECT":
                summary["direct_identifiers"] += 1
            else:
                summary["indirect_identifiers"] += 1

        return summary

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------
    def validate(self, input_text: str):
        try:
            findings = self.scan(input_text)
            summary = self.build_summary(findings)

            status = "PASS" if summary["total_findings"] == 0 else "FAIL"

            result = {
                "status": status,
                "findings": findings,
                "summary": summary
            }

            logging.info("validation completed")
            logging.info(f"total findings: {summary['total_findings']}")

            return result

        except Exception as e:
            logging.error(f"validation failed: {e}")
            return {
                "status": "FAIL",
                "findings": [],
                "summary": {"total_findings": 0}
            }


# ------------------------------------------------------------
# CLI ENTRYPOINT
# ------------------------------------------------------------
if __name__ == "__main__":
    verifier = PIIVerifier()

    if len(sys.argv) > 1:
        text_input = sys.argv[1]
    else:
        text_input = sys.stdin.read()

    verifier.validate(text_input)