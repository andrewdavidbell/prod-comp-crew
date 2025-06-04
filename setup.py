"""
Setup Script for AI Product Research System

This script installs all required dependencies using uv.
"""

import subprocess
import sys
from pathlib import Path


def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "uv", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_uv():
    """Install uv if not already installed."""
    print("Installing uv package manager...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "uv"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("✅ uv installed successfully")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Failed to install uv: {e}")
        return False


def install_dependencies():
    """Install dependencies using uv."""
    requirements_path = Path("requirements.txt")

    if not requirements_path.exists():
        print(f"❌ Requirements file not found at {requirements_path}")
        return False

    print("Installing dependencies using uv...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uv",
                "pip",
                "install",
                "-r",
                str(requirements_path),
            ],
            check=True,
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")

    if env_path.exists():
        print("✅ .env file already exists")
        return True

    print("Creating .env file template...")
    try:
        with open(env_path, "w") as f:
            f.write("OPENROUTER_API_KEY=your_openrouter_api_key_here\n")
            f.write("SERPER_API_KEY=your_serper_api_key_here\n")

        print("✅ .env file created")
        print("⚠️ Please edit the .env file and add your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path("output")

    if output_dir.exists():
        print("✅ output directory already exists")
        return True

    print("Creating output directory...")
    try:
        output_dir.mkdir()
        print("✅ output directory created")
        return True
    except Exception as e:
        print(f"❌ Failed to create output directory: {e}")
        return False


def setup():
    """Run the setup process."""
    print("Setting up AI Product Research System...\n")

    # Check and install uv if needed
    if not check_uv_installed():
        if not install_uv():
            print("❌ Setup failed: Could not install uv")
            return False
    else:
        print("✅ uv is already installed")

    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return False

    # Create .env file if needed
    create_env_file()

    # Create output directory if needed
    create_output_directory()

    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file and add your API keys")
    print("2. Run the validation script: python src/validate_system.py")
    print("3. Try the example: python src/example.py")

    return True


if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
