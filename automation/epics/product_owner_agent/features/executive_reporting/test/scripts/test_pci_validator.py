import logging
from src.util.pci_validator import PCIValidator

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
    validator = PCIValidator()

    logging.info("=" * 80)
    logging.info(f"TEST CASE START: {test_id}")
    logging.info("=" * 80)

    result = validator.validate(input_text)

    total = result["summary"].get("total_findings", 0)

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
        "PAN + CVV",
        "Card 4111 1111 1111 1111 CVV: 123",
        expected_min_findings=2
    )

    run_test_case(
        "EXPIRATION DATE",
        "Card 5500 0000 0000 0004 Expiration: 12/25",
        expected_min_findings=1
    )

    run_test_case(
        "MASKED PAN",
        "User card XXXX-XXXX-XXXX-1111 used today",
        expected_min_findings=1
    )

    run_test_case(
        "PIN + TRACK DATA",
        "ATM PIN: 1234 TRACK-1 data detected",
        expected_min_findings=2
    )

    run_test_case(
        "TRANSACTION REFERENCES",
        "TXN-12345 and PAYMENT-99999 completed successfully",
        expected_min_findings=2
    )

    run_test_case(
        "CLEAN TEXT",
        "This is a normal sentence with no sensitive information.",
        expected_min_findings=0
    )