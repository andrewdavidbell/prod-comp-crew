"""
AI Product Research System

Main entry point for the AI Product Research System.
This script initializes the system and runs the product comparison.
"""

import argparse
import sys
from pathlib import Path

from crew import ProductResearchCrew
from error_handling import (
    ConfigurationError,
    ErrorHandler,
    SystemError,
    handle_error,
    log_error,
)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Product Research System - Compare products objectively"
    )

    parser.add_argument(
        "products",
        nargs="+",
        help="List of products to compare (2-5 products)",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run system validation before starting",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/comparison.md",
        help="Path to save the comparison report (default: output/comparison.md)",
    )

    args = parser.parse_args()

    # Validate number of products
    if len(args.products) < 2 or len(args.products) > 5:
        parser.error("You must specify between 2 and 5 products to compare")

    return args


def run_validation():
    """Run system validation."""
    print("Running system validation...")

    try:
        from validate_system import TESTS, run_test

        # Run all tests
        results = []
        for test in TESTS:
            result = run_test(test)
            results.append(result)
            print(f"\n{test['name']}: {'✅ Passed' if result else '❌ Failed'}")

        if not all(results):
            error_msg = "\n❌ System validation failed. Please fix the issues before continuing."
            print(error_msg)
            raise ConfigurationError(error_msg)

        print("\n✅ System validation passed!")
        return True

    except ImportError as e:
        log_error(
            ConfigurationError(
                "Could not import validation module. Skipping validation.",
                details={"error": str(e)},
            )
        )
        return True  # Continue anyway
    except Exception as e:
        if not isinstance(e, SystemError):
            e = ConfigurationError(f"Error during validation: {e}")
        log_error(e)
        return False


def main():
    """Main entry point."""
    try:
        args = parse_arguments()

        # Run validation if requested
        if args.validate:
            if not run_validation():
                sys.exit(1)

        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(exist_ok=True)

        # Print system information
        print("\nAI Product Research System")
        print("=" * 80)
        print(f"Comparing {len(args.products)} products: {', '.join(args.products)}")
        print(f"Output will be saved to: {output_path}")
        print("=" * 80)

        # Initialize the crew
        crew = ProductResearchCrew(args.products)

        # Run the comparison
        with ErrorHandler(
            context={"products": args.products, "output_path": str(output_path)}
        ) as handler:
            print("\nStarting product comparison...")
            result = crew.kickoff()

            # Save the result to the specified output file
            with open(output_path, "w") as f:
                # Convert result to string if it's not already a string
                result_str = str(result)
                f.write(result_str)

            print(f"\n✅ Comparison complete! Results saved to {output_path}")

        if handler.has_error:
            return 1

        return 0

    except Exception as e:
        error_response = handle_error(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
