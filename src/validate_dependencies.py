"""
Dependency Validation Script

This script validates that all required dependencies are installed
and accessible for the AI Product Research System.
"""

import importlib
import subprocess
import sys


def check_dependency(module_name, package_name=None):
    """Check if a dependency is installed and importable."""
    if package_name is None:
        package_name = module_name

    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name} is installed and accessible")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed or not accessible")
        return False


def install_dependency(package_name):
    """Install a dependency using uv."""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "uv", "pip", "install", package_name]
        )
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False


def validate_dependencies():
    """Validate all required dependencies."""
    # Define dependencies as (module_name, package_name) tuples
    dependencies = [
        ("crewai", "crewai"),
        ("crewai_tools", "crewai-tools"),
        ("dotenv", "python-dotenv"),
        ("langchain_openai", "langchain-openai"),
        ("yaml", "pyyaml"),
        ("pytest", "pytest"),
        ("ruff", "ruff"),
    ]

    missing_deps = []

    # Check each dependency
    for module_name, package_name in dependencies:
        if not check_dependency(module_name, package_name):
            missing_deps.append(package_name)

    # Install missing dependencies
    if missing_deps:
        print("\nMissing dependencies detected. Installing...")
        for package in missing_deps:
            install_dependency(package)

        # Verify installation
        print("\nVerifying installations...")
        still_missing = []
        for module_name, package_name in dependencies:
            if not check_dependency(module_name, package_name):
                still_missing.append(package_name)

        if still_missing:
            print("\n❌ The following dependencies could not be installed:")
            for package in still_missing:
                print(f"  - {package}")
            return False

    print("\n✅ All dependencies are installed and accessible")
    return True


def check_environment_variables():
    """Check if required environment variables are set."""
    import os

    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    required_vars = ["OPENROUTER_API_KEY", "SERPER_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("\n❌ The following environment variables are missing:")
        for var in missing_vars:
            print(f"  - {var}")
        return False

    print("\n✅ All required environment variables are set")
    return True


if __name__ == "__main__":
    print("Validating dependencies for AI Product Research System...\n")

    deps_valid = validate_dependencies()

    if deps_valid:
        env_valid = check_environment_variables()
    else:
        env_valid = False

    if deps_valid and env_valid:
        print("\n✅ System is ready to use!")
        sys.exit(0)
    else:
        print("\n❌ System setup is incomplete. Please resolve the issues above.")
        sys.exit(1)
