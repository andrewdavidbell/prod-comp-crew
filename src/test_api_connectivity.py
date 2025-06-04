"""
API Connectivity Test Script

This script tests the connectivity to the required APIs:
1. OpenRouter API for LLM access
2. Serper API for web search capabilities
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_openrouter_connectivity():
    """Test connectivity to OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ OpenRouter API key not found in environment variables")
        return False

    print("Testing OpenRouter API connectivity...")

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Check if we got a valid response
        models = response.json()
        if "data" in models and len(models["data"]) > 0:
            print("✅ Successfully connected to OpenRouter API")
            print(f"   Available models: {len(models['data'])}")

            # Check if our target model is available
            target_model = "openai/gpt-3.5-turbo"
            model_found = any(model["id"] == target_model for model in models["data"])

            if model_found:
                print(f"✅ Target model '{target_model}' is available")
            else:
                print(f"⚠️ Target model '{target_model}' not found in available models")
                print("   Available models:")
                for model in models["data"]:
                    print(f"   - {model['id']}")

            return True
        else:
            print(
                "❌ Connected to OpenRouter API but received unexpected response format"
            )
            print(f"   Response: {json.dumps(models, indent=2)}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error when connecting to OpenRouter API: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to OpenRouter API: Connection Error")
        return False
    except requests.exceptions.Timeout:
        print("❌ Failed to connect to OpenRouter API: Timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to OpenRouter API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error when testing OpenRouter API: {e}")
        return False


def test_serper_connectivity():
    """Test connectivity to Serper API."""
    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        print("❌ Serper API key not found in environment variables")
        return False

    print("\nTesting Serper API connectivity...")

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": "AI product comparison", "gl": "us", "hl": "en"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # Check if we got a valid response
        search_results = response.json()
        if "organic" in search_results and len(search_results["organic"]) > 0:
            print("✅ Successfully connected to Serper API")
            print(
                f"   Search results: {len(search_results['organic'])} organic results"
            )
            return True
        else:
            print("❌ Connected to Serper API but received unexpected response format")
            print(f"   Response: {json.dumps(search_results, indent=2)}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error when connecting to Serper API: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to Serper API: Connection Error")
        return False
    except requests.exceptions.Timeout:
        print("❌ Failed to connect to Serper API: Timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Serper API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error when testing Serper API: {e}")
        return False


if __name__ == "__main__":
    print("Testing API connectivity for AI Product Research System...\n")

    openrouter_success = test_openrouter_connectivity()
    serper_success = test_serper_connectivity()

    print("\nAPI Connectivity Test Results:")
    print(f"OpenRouter API: {'✅ Connected' if openrouter_success else '❌ Failed'}")
    print(f"Serper API: {'✅ Connected' if serper_success else '❌ Failed'}")

    if openrouter_success and serper_success:
        print("\n✅ All API connections successful!")
        sys.exit(0)
    else:
        print(
            "\n❌ Some API connections failed. Please check your API keys and try again."
        )
        sys.exit(1)
