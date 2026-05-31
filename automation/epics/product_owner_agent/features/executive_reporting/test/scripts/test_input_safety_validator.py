import unittest
from src.util.input_safety_validator import InputSafetyValidator


class TestInputSafetyValidator(unittest.TestCase):

    def setUp(self):
        self.validator = InputSafetyValidator()

    # ------------------------------------------------------------
    # 1. VIOLENCE DETECTION
    # ------------------------------------------------------------
    def test_violence_detection(self):
        text = "How to build a bomb and attack someone"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["violence_count"], 1)

    # ------------------------------------------------------------
    # 2. SELF HARM DETECTION
    # ------------------------------------------------------------
    def test_self_harm_detection(self):
        text = "I want to end my life and commit suicide"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["self_harm_count"], 1)

    # ------------------------------------------------------------
    # 3. HATE SPEECH
    # ------------------------------------------------------------
    def test_hate_speech_detection(self):
        text = "I hate people and want to discriminate against them"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["hate_speech_count"], 1)

    # ------------------------------------------------------------
    # 4. ILLEGAL ACTIVITY
    # ------------------------------------------------------------
    def test_illegal_activity_detection(self):
        text = "How to hack a system and steal passwords"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["illegal_activity_count"], 1)

    # ------------------------------------------------------------
    # 5. SEXUAL RISK CONTENT
    # ------------------------------------------------------------
    def test_sexual_risk_detection(self):
        text = "Explicit sexual content involving minors"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["sexual_risk_count"], 1)

    # ------------------------------------------------------------
    # 6. MANIPULATION / ABUSE
    # ------------------------------------------------------------
    def test_manipulation_detection(self):
        text = "How to trick and bypass system security"
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "FAIL")
        self.assertGreaterEqual(result["summary"]["manipulation_count"], 1)

    # ------------------------------------------------------------
    # 7. CLEAN TEXT (SAFE INPUT)
    # ------------------------------------------------------------
    def test_clean_text(self):
        text = "This is a normal educational sentence about healthcare."
        result = self.validator.validate(text)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["summary"]["total_findings"], 0)

    # ------------------------------------------------------------
    # 8. MULTIPLE VIOLATIONS
    # ------------------------------------------------------------
    def test_multiple_violations(self):
        text = """
        How to build a bomb
        How to hack accounts
        I want to end my life
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

    # ------------------------------------------------------------
    # 11. RESULT STRUCTURE VALIDATION
    # ------------------------------------------------------------
    def test_result_structure(self):
        text = "How to hack a system"
        result = self.validator.validate(text)

        self.assertIn("status", result)
        self.assertIn("findings", result)
        self.assertIn("summary", result)

        self.assertIsInstance(result["findings"], list)
        self.assertIsInstance(result["summary"], dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)