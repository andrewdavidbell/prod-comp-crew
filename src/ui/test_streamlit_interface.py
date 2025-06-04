"""
Unit tests for Streamlit chat interface functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.streamlit_app import StreamlitChatInterface


class TestStreamlitChatInterface:
    """Test cases for StreamlitChatInterface class."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('src.ui.streamlit_app.st'):
            self.interface = StreamlitChatInterface()

    def test_extract_products_from_text_simple_comparison(self):
        """Test product extraction from simple comparison text."""
        test_cases = [
            ("Compare iPhone 15 and Samsung Galaxy S24", ["Iphone 15", "Samsung Galaxy S24"]),
            ("compare macbook pro vs dell xps 13", ["Macbook Pro", "Dell Xps 13"]),
            ("Tell me about Tesla Model 3 versus BMW i4", ["Tesla Model 3", "Bmw I4"]),
        ]

        for input_text, expected in test_cases:
            result = self.interface.extract_products_from_text(input_text)
            assert result is not None, f"Failed to extract products from: {input_text}"
            assert len(result) == 2, f"Expected 2 products, got {len(result)} from: {input_text}"
            # Check that products are extracted (exact match after title case conversion)
            assert result[0] == expected[0], f"First product mismatch: expected {expected[0]}, got {result[0]}"
            assert result[1] == expected[1], f"Second product mismatch: expected {expected[1]}, got {result[1]}"

    def test_extract_products_from_text_multiple_products(self):
        """Test product extraction from text with multiple products."""
        input_text = "Research iPhone 15, Samsung Galaxy S24, and Google Pixel 8"
        result = self.interface.extract_products_from_text(input_text)

        assert result is not None, "Failed to extract products from multiple product text"
        assert len(result) == 3, f"Expected 3 products, got {len(result)}"

        # Check that all products are present
        expected_products = ["iphone", "samsung", "google"]
        for expected in expected_products:
            assert any(expected in product.lower() for product in result), f"Product containing '{expected}' not found in {result}"

    def test_extract_products_from_text_invalid_input(self):
        """Test product extraction from invalid input."""
        invalid_inputs = [
            "Hello there",
            "What's the weather like?",
            "Compare",  # No products specified
            "Tell me about stuff",
            "",
        ]

        for invalid_input in invalid_inputs:
            result = self.interface.extract_products_from_text(invalid_input)
            assert result is None, f"Should return None for invalid input: {invalid_input}"

    def test_extract_products_from_text_edge_cases(self):
        """Test product extraction edge cases."""
        # Too many products (more than 5)
        input_text = "Compare A, B, C, D, E, F, G"
        result = self.interface.extract_products_from_text(input_text)
        assert result is None, "Should return None for more than 5 products"

        # Single product (less than 2)
        input_text = "Tell me about iPhone"
        result = self.interface.extract_products_from_text(input_text)
        assert result is None, "Should return None for single product"

    @patch('src.ui.streamlit_app.os.getenv')
    def test_check_api_configuration_all_present(self, mock_getenv):
        """Test API configuration check when all keys are present."""
        mock_getenv.side_effect = lambda key: "test_key" if key in ["OPENROUTER_API_KEY", "SERPER_API_KEY"] else None

        result = self.interface.check_api_configuration()
        assert result is True, "Should return True when all API keys are configured"

    @patch('src.ui.streamlit_app.os.getenv')
    def test_check_api_configuration_missing_keys(self, mock_getenv):
        """Test API configuration check when keys are missing."""
        mock_getenv.return_value = None  # All keys missing

        with patch('src.ui.streamlit_app.st'):
            result = self.interface.check_api_configuration()
            assert result is False, "Should return False when API keys are missing"

    @patch('src.ui.streamlit_app.os.getenv')
    def test_check_api_configuration_partial_keys(self, mock_getenv):
        """Test API configuration check when some keys are missing."""
        mock_getenv.side_effect = lambda key: "test_key" if key == "OPENROUTER_API_KEY" else None

        with patch('src.ui.streamlit_app.st'):
            result = self.interface.check_api_configuration()
            assert result is False, "Should return False when some API keys are missing"


if __name__ == "__main__":
    pytest.main([__file__])
