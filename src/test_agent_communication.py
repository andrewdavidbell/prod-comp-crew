"""
Agent Communication Test Script

This script tests basic communication with the LLM to ensure
it can respond to simple prompts.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# Load environment variables
load_dotenv()


def test_agent_communication():
    """Test basic communication with the LLM."""
    print("Testing basic LLM communication...")

    # Create a simple LLM instance
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key and api_key.strip():
        api_key = SecretStr(api_key)
    else:
        api_key = None

    # Use a more reliable model
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="openai/gpt-3.5-turbo",
        temperature=0.1,  # Lower temperature for more predictable responses
    )

    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Test simple prompt
    try:
        print("\nSending a simple prompt to the LLM...")

        # Create a simple prompt
        messages = [
            HumanMessage(
                content="List three common methods for comparing tech products."
            )
        ]

        # Get response from LLM
        response = llm.invoke(messages)

        # Save the result to a file
        output_file = output_dir / "agent_communication_test.md"
        response_str = str(response.content)
        with open(output_file, "w") as f:
            f.write(response_str)

        print("\n✅ LLM communication test successful!")
        print(f"   Response: {response_str[:100]}...")
        print(f"   Full response saved to {output_file}")
        return True

    except Exception as e:
        print(f"\n❌ LLM communication test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing LLM communication for AI Product Research System...\n")

    success = test_agent_communication()

    if success:
        print("\n✅ LLM communication test passed!")
        exit(0)
    else:
        print("\n❌ LLM communication test failed!")
        exit(1)
