"""
System Validation Script

This script runs all validation tests for the AI Product Research System
to ensure it's properly set up and ready for use.
"""

import subprocess
import sys
from pathlib import Path

# Define test scripts
TESTS = [
    {
        "name": "Dependency Validation",
        "script": "validate_dependencies.py",
        "description": "Validates that all required dependencies are installed",
    },
    {
        "name": "API Connectivity Test",
        "script": "test_api_connectivity.py",
        "description": "Tests connectivity to OpenRouter and Serper APIs",
    },
    {
        "name": "Agent Communication Test",
        "script": "test_agent_communication.py",
        "description": "Tests basic communication between agents",
    },
]


def run_test(test):
    """Run a test script and return the result."""
    script_path = Path(__file__).parent / test["script"]

    print(f"\n{'=' * 80}")
    print(f"Running {test['name']}: {test['description']}")
    print(f"{'=' * 80}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        # Print the output
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running {test['name']}: {e}")
        return False


def update_development_plan(results):
    """Update the development plan with test results."""
    dev_plan_path = Path(__file__).parent.parent / "cline-docs" / "development-plan.md"

    if not dev_plan_path.exists():
        print(f"Development plan not found at {dev_plan_path}")
        return False

    try:
        with open(dev_plan_path, "r") as f:
            content = f.read()

        # Update dependency installation validation
        if results[0]:  # Dependency validation
            content = content.replace(
                "- [ ] Dependency installation validation",
                "- [x] Dependency installation validation",
            )

        # Update Serper search validation
        if results[1]:  # API connectivity test
            content = content.replace(
                "- [ ] Serper search validation", "- [x] Serper search validation"
            )

        # Update basic agent communication tests
        if results[2]:  # Agent communication test
            content = content.replace(
                "- [ ] Basic agent communication tests",
                "- [x] Basic agent communication tests",
            )

        with open(dev_plan_path, "w") as f:
            f.write(content)

        print(f"\nDevelopment plan updated at {dev_plan_path}")
        return True

    except Exception as e:
        print(f"Error updating development plan: {e}")
        return False


def create_output_directory():
    """Create the output directory if it doesn't exist."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir.exists()


if __name__ == "__main__":
    print("Running system validation for AI Product Research System...\n")

    # Create output directory
    if not create_output_directory():
        print("❌ Failed to create output directory")
        sys.exit(1)

    # Run all tests
    results = []
    for test in TESTS:
        result = run_test(test)
        results.append(result)
        print(f"\n{test['name']}: {'✅ Passed' if result else '❌ Failed'}")

    # Update development plan
    update_development_plan(results)

    # Print summary
    print("\n" + "=" * 80)
    print("System Validation Summary")
    print("=" * 80)

    all_passed = all(results)
    for i, test in enumerate(TESTS):
        status = "✅ Passed" if results[i] else "❌ Failed"
        print(f"{test['name']}: {status}")

    print(
        "\nOverall Status:",
        "✅ All tests passed!" if all_passed else "❌ Some tests failed",
    )

    if all_passed:
        print("\n✅ System is ready for use!")
        sys.exit(0)
    else:
        print("\n❌ System setup is incomplete. Please resolve the issues above.")
        sys.exit(1)
