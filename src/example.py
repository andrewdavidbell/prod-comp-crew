"""
Example Script for AI Product Research System

This script demonstrates how to use the AI Product Research System
with a simple example comparing smartphones.
"""

import sys
from pathlib import Path

from crew import ProductResearchCrew
from error_handling import ErrorHandler, handle_error


def run_example():
    """Run an example product comparison."""
    # Example products to compare
    products = ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8"]

    print("\nAI Product Research System - Example")
    print("=" * 80)
    print(f"Comparing {len(products)} products: {', '.join(products)}")
    print("=" * 80)

    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "example_comparison.md"

    # Initialize the crew
    crew = ProductResearchCrew(products)

    # Run the comparison
    with ErrorHandler(context={"operation": "example_comparison"}) as handler:
        print("\nStarting product comparison...")
        result = crew.kickoff()

        # Save the result to the output file
        with open(output_path, "w") as f:
            # Convert result to string if it's not already a string
            result_str = str(result)
            f.write(result_str)

        print(f"\n✅ Example comparison complete! Results saved to {output_path}")

        # Print a preview of the result
        print("\nPreview of the comparison report:")
        print("-" * 80)
        preview_lines = result_str.split("\n")[:20]  # First 20 lines
        print("\n".join(preview_lines))
        print("...")
        print("-" * 80)
        print(f"Full report available at: {output_path}")

    if handler.has_error:
        return 1

    return 0


if __name__ == "__main__":
    try:
        # Check if dependencies are installed
        try:
            from validate_dependencies import validate_dependencies

            print("Checking dependencies...")
            if not validate_dependencies():
                print("\n❌ Dependencies are not properly installed.")
                print("   Please run: pip install -r requirements.txt")
                sys.exit(1)

        except ImportError:
            print("⚠️ Could not validate dependencies. Continuing anyway...")

        # Run the example
        sys.exit(run_example())
    except Exception as e:
        error_response = handle_error(e)
        sys.exit(1)
