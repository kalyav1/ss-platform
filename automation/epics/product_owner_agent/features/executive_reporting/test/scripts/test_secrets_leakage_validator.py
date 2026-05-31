import unittest

from src.util.secrets_leakage_validator import SecretsLeakageValidator


class TestSecretsLeakageValidator(unittest.TestCase):

    def setUp(self):
        self.validator = SecretsLeakageValidator()

    # -------------------------
    # API KEYS
    # -------------------------
    def test_api_keys_detection(self):
        text = "Here is key sk-1234567890abcdef"
        result = self.validator.scan_text(text)

        self.assertGreater(len(result), 0)
        self.assertTrue(any(r["category"] == "API_KEYS" for r in result))

    # -------------------------
    # AWS KEYS
    # -------------------------
    def test_aws_credentials(self):
        text = "AWS key AKIAABCDEFGHIJKLMNOP and secret aws_secret_access_key=abcd1234abcd1234abcd"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "AWS_CREDENTIALS" for r in result))

    # -------------------------
    # JWT
    # -------------------------
    def test_jwt_detection(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def"
        text = f"token={jwt}"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "JWT_TOKENS" for r in result))

    # -------------------------
    # OAUTH
    # -------------------------
    def test_oauth_detection(self):
        text = "access_token=abcd1234 refresh_token=xyz987"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "OAUTH_TOKENS" for r in result))

    # -------------------------
    # DB CONNECTION STRINGS
    # -------------------------
    def test_db_connection_detection(self):
        text = "postgresql://user:password@localhost:5432/db"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "DATABASE_CONNECTION_STRINGS" for r in result))

    # -------------------------
    # PRIVATE KEY
    # -------------------------
    def test_private_key_detection(self):
        text = "-----BEGIN PRIVATE KEY-----\nABCDEF\n-----END PRIVATE KEY-----"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "PRIVATE_KEYS" for r in result))

    # -------------------------
    # CLOUD TOKENS
    # -------------------------
    def test_cloud_tokens(self):
        text = "type: service_account azure_storage_key=abcd"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "CLOUD_TOKENS" for r in result))

    # -------------------------
    # DEVOPS SECRETS
    # -------------------------
    def test_devops_secrets(self):
        text = "GITHUB_TOKEN=abc123 TF_TOKEN=xyz789"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "DEVOPS_SECRETS" for r in result))

    # -------------------------
    # ENV SECRETS
    # -------------------------
    def test_env_secrets(self):
        text = "PASSWORD=secret123 DB_PASSWORD=pass456"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "ENV_SECRETS" for r in result))

    # -------------------------
    # HIGH ENTROPY
    # -------------------------
    def test_high_entropy(self):
        text = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
        result = self.validator.scan_text(text)

        self.assertTrue(any(r["category"] == "HIGH_ENTROPY" for r in result))

    # -------------------------
    # MULTILINE INPUT
    # -------------------------
    def test_multiline_input(self):
        text = """
        normal text
        sk-1234567890abcdef
        postgres://user:pass@localhost/db
        """
        result = self.validator.scan_text(text)

        self.assertGreaterEqual(len(result), 2)

    # -------------------------
    # EMPTY INPUT
    # -------------------------
    def test_empty_input(self):
        result = self.validator.scan_text("")
        self.assertEqual(result, [])

    # -------------------------
    # NONE INPUT
    # -------------------------
    def test_none_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result["summary"]["status"], "PASS")

    # -------------------------
    # REDACTION CHECK
    # -------------------------
    def test_redaction(self):
        text = "sk-live-abcdefghijklmnopqrstuvwxyz1234567890"
        result = self.validator.scan_text(text)

        for r in result:
            self.assertIn("*", r["match"])
            self.assertLess(len(r["match"]), len(text))

    # -------------------------
    # SUMMARY VALIDATION
    # -------------------------
    def test_summary_structure(self):
        text = "sk-1234567890abcdef"
        result = self.validator.validate(text)

        summary = result["summary"]

        expected_keys = [
            "total_findings",
            "api_key_count",
            "aws_credential_count",
            "jwt_count",
            "oauth_token_count",
            "database_connection_count",
            "private_key_count",
            "cloud_token_count",
            "devops_secret_count",
            "environment_secret_count",
            "high_entropy_secret_count",
            "risk_score",
            "status",
        ]

        for key in expected_keys:
            self.assertIn(key, summary)

    # -------------------------
    # DEDUPLICATION TEST
    # -------------------------
    def test_deduplication(self):
        text = "sk-1234567890abcdef sk-1234567890abcdef"
        result = self.validator.scan_text(text)

        # Should not duplicate identical findings
        matches = [r["match"] for r in result]
        self.assertLessEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)