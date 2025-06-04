"""
Streamlit Chat Interface for AI Product Research System

A user-friendly web interface for conducting product comparisons through natural conversation.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv

# Add src directory to path for imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from crew import ProductResearchCrew
from error_handling import (
    ConfigurationError,
    ErrorHandler,
    SystemError,
    handle_error,
    log_error,
)

# Load environment variables
load_dotenv()


class StreamlitChatInterface:
    """Streamlit chat interface for the product research system."""

    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()

    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="AI Product Research Chat",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def initialize_session_state(self):
        """Initialize session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        if "current_research" not in st.session_state:
            st.session_state.current_research = None

        if "api_keys_configured" not in st.session_state:
            st.session_state.api_keys_configured = self.check_api_configuration()

    def check_api_configuration(self) -> bool:
        """Check if required API keys are configured."""
        required_keys = ["OPENROUTER_API_KEY", "SERPER_API_KEY"]
        missing_keys = []

        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)

        if missing_keys:
            st.session_state.missing_api_keys = missing_keys
            return False

        return True

    def extract_products_from_text(self, text: str) -> Optional[List[str]]:
        """Extract product names from natural language input."""
        text_lower = text.lower().strip()

        # Pattern 1: "compare X and Y" or "compare X vs Y"
        pattern1 = r"compare\s+(.+?)\s+(?:and|vs|versus)\s+(.+?)(?:\s*$|[.!?])"
        match1 = re.search(pattern1, text_lower)
        if match1:
            product1 = match1.group(1).strip().title()
            product2 = match1.group(2).strip().title()
            if product1 and product2:
                return [product1, product2]

        # Pattern 2: "tell me about X vs Y" or "research X versus Y"
        pattern2 = r"(?:tell me about|research)\s+(.+?)\s+(?:vs|versus)\s+(.+?)(?:\s*$|[.!?])"
        match2 = re.search(pattern2, text_lower)
        if match2:
            product1 = match2.group(1).strip().title()
            product2 = match2.group(2).strip().title()
            if product1 and product2:
                return [product1, product2]

        # Pattern 3: "compare/research X, Y, and Z" (comma-separated list)
        pattern3 = r"(?:compare|research)\s+(.+?)(?:\s*$|[.!?])"
        match3 = re.search(pattern3, text_lower)
        if match3:
            products_text = match3.group(1).strip()
            # Split by commas and "and"
            products_raw = re.split(r',\s*(?:and\s+)?|,?\s+and\s+', products_text)
            products = []
            for product in products_raw:
                product = product.strip()
                if product and len(product) > 1:
                    products.append(product.title())

            if 2 <= len(products) <= 5:
                return products

        return None

    def display_welcome_message(self):
        """Display welcome message and instructions."""
        st.title("🔍 AI Product Research Chat")
        st.markdown("""
        Welcome to the AI Product Research System! I can help you compare products objectively
        by researching their specifications, features, and characteristics.

        **How to use:**
        - Ask me to compare 2-5 products (e.g., "Compare iPhone 15 and Samsung Galaxy S24")
        - I'll research each product and provide a comprehensive comparison
        - You can download the results as a markdown report

        **Example requests:**
        - "Compare MacBook Pro and Dell XPS 13"
        - "Research iPhone 15, Samsung Galaxy S24, and Google Pixel 8"
        - "Tell me about Tesla Model 3 vs BMW i4"
        """)

    def display_api_configuration_warning(self):
        """Display API configuration warning."""
        st.error("⚠️ API Configuration Required")
        st.markdown("""
        The following API keys are missing from your environment:
        """)

        for key in st.session_state.missing_api_keys:
            st.code(key)

        st.markdown("""
        Please configure these API keys in your environment variables or `.env` file:

        ```bash
        OPENROUTER_API_KEY=your_openrouter_key_here
        SERPER_API_KEY=your_serper_key_here
        ```

        After configuring the keys, restart the application.
        """)

    def display_chat_interface(self):
        """Display the main chat interface."""
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me to compare some products..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process the request
            self.process_user_request(prompt)

    def process_user_request(self, user_input: str):
        """Process user request and generate response."""
        with st.chat_message("assistant"):
            # Try to extract products from the input
            products = self.extract_products_from_text(user_input)

            if not products:
                response = """
                I couldn't identify specific products to compare in your request.

                Please try asking me to compare specific products, for example:
                - "Compare iPhone 15 and Samsung Galaxy S24"
                - "Research MacBook Pro, Dell XPS 13, and ThinkPad X1"
                - "Tell me about Tesla Model 3 vs BMW i4"
                """
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return

            # Confirm the products identified
            products_text = ", ".join(products)
            st.markdown(f"I'll research and compare: **{products_text}**")

            # Show progress indicator
            with st.spinner("Researching products... This may take a few minutes."):
                try:
                    # Initialize the research crew
                    crew = ProductResearchCrew(products)

                    # Run the research
                    with ErrorHandler(context={"products": products}) as handler:
                        result = crew.kickoff()

                        if handler.has_error:
                            st.error("An error occurred during research. Please check the logs.")
                            return

                        # Display results
                        result_str = str(result)
                        st.markdown("## Research Results")
                        st.markdown(result_str)

                        # Store results for download
                        st.session_state.current_research = {
                            "products": products,
                            "result": result_str,
                            "timestamp": st.session_state.get("timestamp", "")
                        }

                        # Add to conversation history
                        response = f"I've completed the research for {products_text}. Here are the results:\n\n{result_str}"
                        st.session_state.messages.append({"role": "assistant", "content": response})

                        # Offer download
                        st.success("✅ Research completed! You can download the full report using the sidebar.")

                except Exception as e:
                    error_msg = f"An error occurred during research: {str(e)}"
                    st.error(error_msg)
                    log_error(SystemError(error_msg))
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    def display_sidebar(self):
        """Display sidebar with additional options."""
        with st.sidebar:
            st.header("Options")

            # Clear conversation button
            if st.button("🗑️ Clear Conversation"):
                st.session_state.messages = []
                st.session_state.current_research = None
                st.rerun()

            # Download results if available
            if st.session_state.current_research:
                st.header("Download Results")

                research = st.session_state.current_research
                products_filename = "_".join(research["products"]).replace(" ", "_")
                filename = f"product_comparison_{products_filename}.md"

                st.download_button(
                    label="📄 Download Report",
                    data=research["result"],
                    file_name=filename,
                    mime="text/markdown"
                )

            # API Status
            st.header("System Status")
            if st.session_state.api_keys_configured:
                st.success("✅ API Keys Configured")
            else:
                st.error("❌ API Keys Missing")

            # Example prompts
            st.header("Example Prompts")
            example_prompts = [
                "Compare iPhone 15 and Samsung Galaxy S24",
                "Research MacBook Pro and Dell XPS 13",
                "Tell me about Tesla Model 3 vs BMW i4",
                "Compare Nintendo Switch, PlayStation 5, and Xbox Series X"
            ]

            for prompt in example_prompts:
                if st.button(f"💡 {prompt}", key=f"example_{hash(prompt)}"):
                    # Add the example prompt to chat
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.rerun()

    def run(self):
        """Run the Streamlit application."""
        # Display sidebar
        self.display_sidebar()

        # Check API configuration
        if not st.session_state.api_keys_configured:
            self.display_api_configuration_warning()
            return

        # Display welcome message if no conversation started
        if not st.session_state.messages:
            self.display_welcome_message()

        # Display chat interface
        self.display_chat_interface()


def main():
    """Main entry point for the Streamlit application."""
    try:
        app = StreamlitChatInterface()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        log_error(SystemError(f"Streamlit application error: {str(e)}"))


if __name__ == "__main__":
    main()
