"""
Data Processing Layer Test Script

This script tests the functionality of the data processing layer:
1. WebScrapingAdapter for extracting product specifications
2. SpecificationExtractor for structuring raw specifications
3. MarketingClaimDetector for filtering marketing claims
4. DataNormalizer for ensuring consistent units and formats
5. DataProcessor as the main orchestration class
"""

import sys
from pathlib import Path

from data_processing import (
    DataNormalizer,
    DataProcessor,
    MarketingClaimDetector,
    SpecificationExtractor,
    WebScrapingAdapter,
)


def create_sample_html():
    """Create sample HTML content for testing."""
    return """
    <html>
        <head>
            <title>Sample Product Page</title>
        </head>
        <body>
            <h1 id="productTitle">Premium XYZ Smartphone - Ultimate Performance</h1>
            <div class="price">£799.99</div>
            <div class="specs-table">
                <table>
                    <tr>
                        <th>Processor</th>
                        <td>Octa-core 2.8GHz with revolutionary AI capabilities</td>
                    </tr>
                    <tr>
                        <th>Memory</th>
                        <td>8GB RAM</td>
                    </tr>
                    <tr>
                        <th>Storage</th>
                        <td>256GB</td>
                    </tr>
                    <tr>
                        <th>Display</th>
                        <td>6.5 inch Super AMOLED (2400 x 1080)</td>
                    </tr>
                    <tr>
                        <th>Battery</th>
                        <td>4500mAh with industry-leading fast charging</td>
                    </tr>
                    <tr>
                        <th>Camera</th>
                        <td>48MP main + 12MP ultra-wide + 5MP macro</td>
                    </tr>
                    <tr>
                        <th>Weight</th>
                        <td>189g</td>
                    </tr>
                </table>
            </div>
        </body>
    </html>
    """


def create_sample_raw_specs():
    """Create sample raw specifications for testing."""
    return {
        "product_name": "Premium XYZ Smartphone - Ultimate Performance",
        "price": "£799.99",
        "source_url": "https://example.com/products/xyz-smartphone",
        "source_domain": "example",
        "specifications": {
            "Processor": "Octa-core 2.8GHz with revolutionary AI capabilities",
            "Memory": "8GB RAM",
            "Storage": "256GB",
            "Display": "6.5 inch Super AMOLED (2400 x 1080)",
            "Battery": "4500mAh with industry-leading fast charging",
            "Camera": "48MP main + 12MP ultra-wide + 5MP macro",
            "Weight": "189g",
        },
    }


def create_sample_structured_specs():
    """Create sample structured specifications for testing."""
    return {
        "product_name": "Premium XYZ Smartphone - Ultimate Performance",
        "price": "£799.99",
        "source_url": "https://example.com/products/xyz-smartphone",
        "source_domain": "example",
        "specifications": {
            "processor": {
                "Processor": "Octa-core 2.8GHz with revolutionary AI capabilities",
            },
            "memory": {
                "Memory": "8GB RAM",
                "Storage": "256GB",
            },
            "display": {
                "Display": "6.5 inch Super AMOLED (2400 x 1080)",
            },
            "battery": {
                "Battery": "4500mAh with industry-leading fast charging",
            },
            "camera": {
                "Camera": "48MP main + 12MP ultra-wide + 5MP macro",
            },
            "other": {
                "Weight": "189g",
            },
        },
    }


def test_web_scraping_adapter():
    """Test the WebScrapingAdapter class."""
    print("\nTesting WebScrapingAdapter...")

    try:
        # Create an instance of WebScrapingAdapter
        adapter = WebScrapingAdapter()

        # Create sample HTML content
        html_content = create_sample_html()
        url = "https://example.com/products/xyz-smartphone"

        # Extract specifications
        specs = adapter.extract_specifications(html_content, url)

        # Validate the extracted specifications
        if not specs:
            print("❌ Failed to extract specifications")
            return False

        if "product_name" not in specs or not specs["product_name"]:
            print("❌ Failed to extract product name")
            return False

        if "price" not in specs or not specs["price"]:
            print("❌ Failed to extract price")
            return False

        if "specifications" not in specs or not specs["specifications"]:
            print("❌ Failed to extract specifications")
            return False

        # Check if source metadata is added
        if "source_url" not in specs or specs["source_url"] != url:
            print("❌ Failed to add source URL")
            return False

        if "source_domain" not in specs or not specs["source_domain"]:
            print("❌ Failed to add source domain")
            return False

        print("✅ WebScrapingAdapter test passed")
        print(f"   Extracted {len(specs['specifications'])} specifications")
        return True

    except Exception as e:
        print(f"❌ WebScrapingAdapter test failed: {e}")
        return False


def test_specification_extractor():
    """Test the SpecificationExtractor class."""
    print("\nTesting SpecificationExtractor...")

    try:
        # Create an instance of SpecificationExtractor
        extractor = SpecificationExtractor()

        # Create sample raw specifications
        raw_specs = create_sample_raw_specs()

        # Extract structured specifications
        structured_specs = extractor.extract_structured_specs(raw_specs, "smartphone")

        # Validate the structured specifications
        if not structured_specs:
            print("❌ Failed to extract structured specifications")
            return False

        if (
            "product_name" not in structured_specs
            or not structured_specs["product_name"]
        ):
            print("❌ Failed to include product name")
            return False

        if "price" not in structured_specs or not structured_specs["price"]:
            print("❌ Failed to include price")
            return False

        if (
            "specifications" not in structured_specs
            or not structured_specs["specifications"]
        ):
            print("❌ Failed to include specifications")
            return False

        # Check if specifications are categorized
        categories = structured_specs["specifications"].keys()
        expected_categories = [
            "processor",
            "memory",
            "display",
            "camera",
            "battery",
            "other",
        ]

        for category in expected_categories:
            if category not in categories:
                print(f"❌ Missing category: {category}")
                return False

        print("✅ SpecificationExtractor test passed")
        print(f"   Categorized specifications into {len(categories)} categories")
        return True

    except Exception as e:
        print(f"❌ SpecificationExtractor test failed: {e}")
        return False


def test_marketing_claim_detector():
    """Test the MarketingClaimDetector class."""
    print("\nTesting MarketingClaimDetector...")

    try:
        # Create an instance of MarketingClaimDetector
        detector = MarketingClaimDetector()

        # Create sample structured specifications
        structured_specs = create_sample_structured_specs()

        # Filter marketing claims
        filtered_specs, marketing_claims = detector.filter_marketing_claims(
            structured_specs
        )

        # Validate the filtered specifications
        if not filtered_specs:
            print("❌ Failed to filter specifications")
            return False

        if not marketing_claims:
            print("❌ Failed to detect marketing claims")
            return False

        # Check if marketing claims are detected in product name
        if (
            "product_name" not in marketing_claims
            or not marketing_claims["product_name"]
        ):
            print("⚠️ No marketing claims detected in product name")

        # Check if marketing claims are detected in specifications
        if "claims" not in marketing_claims or not marketing_claims["claims"]:
            print("⚠️ No marketing claims detected in specifications")

        # Test the detect_marketing_claims method directly
        test_text = "Revolutionary AI capabilities with industry-leading performance"
        is_marketing, confidence, phrases = detector.detect_marketing_claims(test_text)

        if not is_marketing:
            print("❌ Failed to detect marketing claims in test text")
            return False

        if not phrases:
            print("❌ Failed to extract marketing phrases")
            return False

        print("✅ MarketingClaimDetector test passed")
        print(f"   Detected {len(phrases)} marketing phrases in test text")
        print(f"   Confidence: {confidence:.2f}")
        return True

    except Exception as e:
        print(f"❌ MarketingClaimDetector test failed: {e}")
        return False


def test_data_normalizer():
    """Test the DataNormalizer class."""
    print("\nTesting DataNormalizer...")

    try:
        # Create an instance of DataNormalizer
        normalizer = DataNormalizer()

        # Test normalization of individual values
        test_cases = [
            ("8GB RAM", "memory", "Memory", "8 GB"),
            ("256GB", "storage", "Storage", "256 GB"),
            ("6.5 inch", "display", "Display", '6.5"'),
            ("2.8GHz", "processor", "Processor", "2.80 GHz"),
            ("4500mAh", "battery", "Battery", "4500 mAh"),
            ("189g", "weight", "Weight", "189 g"),
            ("1TB", "storage", "Storage", "1024 GB"),
            ("16.5cm", "display", "Display", '6.5"'),
            ("2400 x 1080", "display", "Resolution", "2400x1080"),
        ]

        for value, category, key, expected in test_cases:
            normalized = normalizer.normalize_value(value, category, key)
            if normalized != expected:
                print(f"❌ Normalization failed for {value}")
                print(f"   Expected: {expected}")
                print(f"   Got: {normalized}")
                return False

        # Test normalization of specifications
        structured_specs = create_sample_structured_specs()
        normalized_specs = normalizer.normalize_specifications(structured_specs)

        if not normalized_specs:
            print("❌ Failed to normalize specifications")
            return False

        if (
            "specifications" not in normalized_specs
            or not normalized_specs["specifications"]
        ):
            print("❌ Failed to include specifications in normalized result")
            return False

        print("✅ DataNormalizer test passed")
        print("   All test cases passed")
        return True

    except Exception as e:
        print(f"❌ DataNormalizer test failed: {e}")
        return False


def test_data_processor():
    """Test the DataProcessor class."""
    print("\nTesting DataProcessor...")

    try:
        # Create an instance of DataProcessor
        processor = DataProcessor()

        # Create sample HTML content
        html_content = create_sample_html()
        url = "https://example.com/products/xyz-smartphone"
        product_category = "smartphone"

        # Process product data
        result = processor.process_product_data(html_content, url, product_category)

        # Validate the processed data
        if not result:
            print("❌ Failed to process product data")
            return False

        if "normalized_specs" not in result or not result["normalized_specs"]:
            print("❌ Missing normalized specifications")
            return False

        if "marketing_claims" not in result or not result["marketing_claims"]:
            print("❌ Missing marketing claims")
            return False

        if "raw_specs" not in result or not result["raw_specs"]:
            print("❌ Missing raw specifications")
            return False

        # Test saving processed data
        product_name = result["normalized_specs"]["product_name"]
        file_path = processor.save_processed_data(result, product_name)

        if not file_path.exists():
            print("❌ Failed to save processed data")
            return False

        # Clean up the test file
        file_path.unlink()

        print("✅ DataProcessor test passed")
        print("   Successfully processed and saved product data")
        return True

    except Exception as e:
        print(f"❌ DataProcessor test failed: {e}")
        return False


def run_all_tests():
    """Run all data processing layer tests."""
    print("Running Data Processing Layer Tests...\n")

    # Create output directory if it doesn't exist
    output_dir = Path("output/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run tests
    web_scraping_adapter_success = test_web_scraping_adapter()
    specification_extractor_success = test_specification_extractor()
    marketing_claim_detector_success = test_marketing_claim_detector()
    data_normalizer_success = test_data_normalizer()
    data_processor_success = test_data_processor()

    # Print summary
    print("\nData Processing Layer Test Results:")
    print(
        f"WebScrapingAdapter: {'✅ Passed' if web_scraping_adapter_success else '❌ Failed'}"
    )
    print(
        f"SpecificationExtractor: {'✅ Passed' if specification_extractor_success else '❌ Failed'}"
    )
    print(
        f"MarketingClaimDetector: {'✅ Passed' if marketing_claim_detector_success else '❌ Failed'}"
    )
    print(f"DataNormalizer: {'✅ Passed' if data_normalizer_success else '❌ Failed'}")
    print(f"DataProcessor: {'✅ Passed' if data_processor_success else '❌ Failed'}")

    # Overall result
    all_passed = (
        web_scraping_adapter_success
        and specification_extractor_success
        and marketing_claim_detector_success
        and data_normalizer_success
        and data_processor_success
    )

    if all_passed:
        print("\n✅ All data processing layer tests passed!")
        return 0
    else:
        print("\n❌ Some data processing layer tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
