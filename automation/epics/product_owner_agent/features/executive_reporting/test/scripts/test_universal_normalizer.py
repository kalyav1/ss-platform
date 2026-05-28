import json
import logging
from src.util.universal_normalizer import process_inputs


# =========================================================
# LOGGING CONFIG
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("universal_normalizer_test")


# =========================================================
# TEST RUNNER
# =========================================================

def run_tests(input_list):

    logger.info("Starting universal normalizer test run")

    result = process_inputs(input_list)

    test_result = {
        "status": result.get("status"),
        "summary": result.get("summary"),
        "normalized_count": len(result.get("normalized_inputs", [])),
        "final_context_length": len(result.get("final_context", "")),
        "has_errors": any(
            item.get("status") == "ERROR"
            for item in result.get("normalized_inputs", [])
        )
    }

    logger.info("Test run completed")
    logger.info(f"Summary: {test_result['summary']}")
    logger.info(f"Normalized items: {test_result['normalized_count']}")
    logger.info(f"Context size: {test_result['final_context_length']}")
    logger.info(f"Has errors: {test_result['has_errors']}")

    return test_result


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    logger.info("No input provided. Exiting test runner.")

    # Replace with real test files generated externally (LLM or fixtures)
    test_inputs = [
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.csv",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.docx",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.json",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.md",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.pdf",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.png",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.pptx",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.txt",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.xlsx",
        r"C:\Users\vijay\OneDrive\Desktop\SS-PLATFORM\automation\epics\product_owner_agent\features\executive_reporting\test\data\universal_normalizer\sample.yaml"
    ]

    output = run_tests(test_inputs)

    logger.info(f"Final output: {json.dumps(output)}")