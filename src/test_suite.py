"""
Automated Test Suite for AI Product Research System

This script runs all tests for the AI Product Research System and generates
a coverage report to ensure code quality and reliability.

Usage:
    python test_suite.py [--coverage] [--performance] [--security]

Options:
    --coverage      Generate a coverage report
    --performance   Run performance benchmarking tests
    --security      Run security validation tests
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Define test modules
UNIT_TESTS = [
    {
        "name": "Data Processing Tests",
        "script": "test_data_processing.py",
        "description": "Tests for the data processing layer",
    },
    {
        "name": "Comparison Engine Tests",
        "script": "test_comparison_engine.py",
        "description": "Tests for the comparison engine",
    },
    {
        "name": "API Connectivity Tests",
        "script": "test_api_connectivity.py",
        "description": "Tests for API connectivity",
    },
    {
        "name": "Agent Communication Tests",
        "script": "test_agent_communication.py",
        "description": "Tests for agent communication",
    },
]

INTEGRATION_TESTS = [
    {
        "name": "End-to-End Integration Tests",
        "script": "test_integration.py",
        "description": "End-to-end integration tests for the complete workflow",
    },
]

PERFORMANCE_TESTS = [
    {
        "name": "Performance Benchmarking",
        "script": "test_performance.py",
        "description": "Performance benchmarking tests",
    },
]

SECURITY_TESTS = [
    {
        "name": "Security Validation",
        "script": "test_security.py",
        "description": "Security validation tests",
    },
]


def run_test(test, verbose=True):
    """Run a test script and return the result."""
    script_path = Path(__file__).parent / test["script"]

    if verbose:
        print(f"\n{'=' * 80}")
        print(f"Running {test['name']}: {test['description']}")
        print(f"{'=' * 80}")

    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        end_time = time.time()
        execution_time = end_time - start_time

        # Print the output
        if verbose:
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            print(f"Execution time: {execution_time:.2f} seconds")

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": execution_time,
        }

    except Exception as e:
        if verbose:
            print(f"Error running {test['name']}: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "execution_time": 0,
        }


def run_coverage(tests):
    """Run tests with coverage and generate a report."""
    print("\n" + "=" * 80)
    print("Running tests with coverage")
    print("=" * 80)

    try:
        # Create a list of test scripts
        test_scripts = [test["script"] for test in tests]
        test_paths = [str(Path(__file__).parent / script) for script in test_scripts]

        # Run coverage
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--source=src",
            "--omit=src/test_*",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(Path(__file__).parent),
            "-p",
            "test_*.py",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        # Print the output
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

        # Generate coverage report
        report_cmd = [sys.executable, "-m", "coverage", "report", "-m"]
        report_result = subprocess.run(
            report_cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        # Print the report
        print("\nCoverage Report:")
        print(report_result.stdout)
        if report_result.stderr:
            print("Errors:")
            print(report_result.stderr)

        # Generate HTML report
        html_cmd = [sys.executable, "-m", "coverage", "html"]
        subprocess.run(html_cmd, check=False)

        print("\nHTML coverage report generated in htmlcov/index.html")

        return result.returncode == 0

    except Exception as e:
        print(f"Error running coverage: {e}")
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run automated tests for AI Product Research System"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate a coverage report",
    )

    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance benchmarking tests",
    )

    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security validation tests",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests (unit, integration, performance, security)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Determine which tests to run
    tests_to_run = []
    tests_to_run.extend(UNIT_TESTS)  # Always run unit tests

    # Add integration tests
    tests_to_run.extend(INTEGRATION_TESTS)

    # Add performance tests if requested
    if args.performance or args.all:
        tests_to_run.extend(PERFORMANCE_TESTS)

    # Add security tests if requested
    if args.security or args.all:
        tests_to_run.extend(SECURITY_TESTS)

    # Run tests with coverage if requested
    if args.coverage or args.all:
        coverage_success = run_coverage(tests_to_run)
    else:
        # Run tests without coverage
        results = []
        for test in tests_to_run:
            result = run_test(test)
            results.append(result)
            print(
                f"\n{test['name']}: {'✅ Passed' if result['success'] else '❌ Failed'} "
                f"({result['execution_time']:.2f}s)"
            )

        # Print summary
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)

        all_passed = all(result["success"] for result in results)
        for i, test in enumerate(tests_to_run):
            status = "✅ Passed" if results[i]["success"] else "❌ Failed"
            print(f"{test['name']}: {status} ({results[i]['execution_time']:.2f}s)")

        print(
            "\nOverall Status:",
            "✅ All tests passed!" if all_passed else "❌ Some tests failed",
        )

        if all_passed:
            print("\n✅ System tests completed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed. Please resolve the issues above.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
