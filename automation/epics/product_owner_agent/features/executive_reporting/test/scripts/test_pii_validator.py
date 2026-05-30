import logging
from src.util.pii_validator import PIIVerifier

# ------------------------------------------------------------
# LOGGING CONFIGURATION
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ------------------------------------------------------------
# TEST RUNNER
# ------------------------------------------------------------
def run_test_case(test_id, input_text, expected_min_findings=1):
    verifier = PIIVerifier()

    logging.info("=" * 80)
    logging.info(f"TEST CASE START: {test_id}")
    logging.info("=" * 80)

    result = verifier.validate(input_text)

    total = result["summary"]["total_findings"]

    logging.info(f"STATUS: {result['status']}")
    logging.info(f"TOTAL FINDINGS: {total}")

    for f in result["findings"]:
        logging.info(f"FINDING: {f}")

    if total >= expected_min_findings:
        logging.info(f"TEST PASSED: {test_id}")
    else:
        logging.error(
            f"TEST FAILED: {test_id} | "
            f"Expected >= {expected_min_findings}, got {total}"
        )


# ------------------------------------------------------------
# TEST SUITE
# ------------------------------------------------------------
if __name__ == "__main__":

    run_test_case(
        "EMAIL + PHONE",
        "Contact john.doe@example.com or call (555) 123-4567",
        expected_min_findings=2
    )

    run_test_case(
        "SSN + ADDRESS",
        "User SSN 123-45-6789 lives at 123 Main Street",
        expected_min_findings=2
    )

    run_test_case(
        "CREDIT CARD + IP",
        "Card 4111 1111 1111 1111 used from 192.168.1.1",
        expected_min_findings=2
    )

    run_test_case(
        "INDIRECT IDS",
        "EMP-12345 assigned to owner=john.smith and device DEV-001",
        expected_min_findings=3
    )

    run_test_case(
        "CLEAN TEXT",
        "This is a normal sentence with no sensitive information.",
        expected_min_findings=0
    )