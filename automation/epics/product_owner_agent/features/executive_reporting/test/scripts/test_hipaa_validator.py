import unittest
import logging
from src.util.hipaa_validator import HIPAAValidator


# ------------------------------------------------------------
# LOGGING (optional for debugging)
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class TestHIPAAValidator(unittest.TestCase):

    def setUp(self):
        # IMPORTANT: instantiate the CLASS, not module
        self.validator = HIPAAValidator()

    # ------------------------------------------------------------
    # 1. PATIENT IDENTIFIERS
    # ------------------------------------------------------------
    def test_patient_identifiers(self):
        text = "Patient: John Smith visited clinic"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["patient_identifiers"], 1)

    # ------------------------------------------------------------
    # 2. MRN
    # ------------------------------------------------------------
    def test_mrn_detection(self):
        text = "MRN: 123456 admitted yesterday"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["medical_record_numbers"], 1)

    # ------------------------------------------------------------
    # 3. INSURANCE ID
    # ------------------------------------------------------------
    def test_insurance_id(self):
        text = "Insurance ID: ABC12345 processed"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["insurance_ids"], 1)

    # ------------------------------------------------------------
    # 4. DIAGNOSIS
    # ------------------------------------------------------------
    def test_diagnosis(self):
        text = "Patient diagnosed with diabetes"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["diagnosis"], 1)

    # ------------------------------------------------------------
    # 5. TREATMENT
    # ------------------------------------------------------------
    def test_treatment(self):
        text = "Chemotherapy scheduled next week"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["treatment_data"], 1)

    # ------------------------------------------------------------
    # 6. PRESCRIPTION
    # ------------------------------------------------------------
    def test_prescription(self):
        text = "Prescribed ibuprofen 10mg dosage"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["prescription_data"], 1)

    # ------------------------------------------------------------
    # 7. CLEAN TEXT
    # ------------------------------------------------------------
    def test_clean_text(self):
        text = "This is a normal sentence."
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["summary"]["total_findings"], 0)

    # ------------------------------------------------------------
    # 8. MULTIPLE FINDINGS
    # ------------------------------------------------------------
    def test_multiple_findings(self):
        text = """
        Patient: John Doe
        MRN: 999999
        Insurance ID: ABC12345
        Diagnosed with cancer
        """

        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["total_findings"], 3)

    # ------------------------------------------------------------
    # 9. EMPTY INPUT
    # ------------------------------------------------------------
    def test_empty_input(self):
        result = self.validator.validate("   ")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["summary"]["total_findings"], 0)

    # ------------------------------------------------------------
    # 10. NONE INPUT
    # ------------------------------------------------------------
    def test_none_input(self):
        result = self.validator.validate(None)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["summary"]["total_findings"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)