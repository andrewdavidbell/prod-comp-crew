"""
Integration Tests for AI Product Research System

This script tests the end-to-end workflow of the AI Product Research System,
ensuring all components work together correctly.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

from comparison_engine import ComparisonEngine
from crew import ProductResearchCrew
from data_processing import DataProcessor, WebScrapingAdapter


class IntegrationTests(TestCase):
    """Integration tests for the AI Product Research System."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)

        # Create sample HTML content for testing
        self.sample_html = self._create_sample_html()
        self.product_url = "https://example.com/products/smartphone-a"
        self.product_category = "smartphone"

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def _create_sample_html(self):
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

    def _create_sample_product_data(self):
        """Create sample product data for testing."""
        return [
            {
                "product_name": "Smartphone A",
                "price": "£799.99",
                "source_url": "https://example.com/products/smartphone-a",
                "source_domain": "example",
                "specifications": {
                    "processor": {
                        "Processor": "Octa-core 2.8GHz",
                    },
                    "memory": {
                        "RAM": "8GB",
                        "Storage": "256GB",
                    },
                    "display": {
                        "Display": '6.5"',
                        "Resolution": "2400x1080",
                    },
                    "battery": {
                        "Battery": "4500 mAh",
                    },
                    "camera": {
                        "Main Camera": "48MP",
                        "Front Camera": "12MP",
                    },
                    "other": {
                        "Weight": "189 g",
                    },
                },
            },
            {
                "product_name": "Smartphone B",
                "price": "£899.99",
                "source_url": "https://example.com/products/smartphone-b",
                "source_domain": "example",
                "specifications": {
                    "processor": {
                        "CPU": "Quad-core 3.0GHz",
                    },
                    "memory": {
                        "Memory": "12GB",
                        "Storage Capacity": "512GB",
                    },
                    "display": {
                        "Screen": '6.7"',
                        "Screen Resolution": "2800x1260",
                    },
                    "battery": {
                        "Battery Capacity": "5000 mAh",
                    },
                    "camera": {
                        "Rear Camera": "64MP",
                        "Selfie Camera": "16MP",
                    },
                    "other": {
                        "Weight": "195 g",
                    },
                },
            },
        ]

    def test_data_processing_to_comparison_integration(self):
        """Test integration between data processing and comparison engine."""
        print("\nTesting Data Processing to Comparison Engine Integration...")

        try:
            # Step 1: Process product data using DataProcessor
            data_processor = DataProcessor()
            processed_data = data_processor.process_product_data(
                self.sample_html, self.product_url, self.product_category
            )

            # Verify processed data
            self.assertIsNotNone(processed_data)
            self.assertIn("normalized_specs", processed_data)
            self.assertIn("marketing_claims", processed_data)
            self.assertIn("raw_specs", processed_data)

            # Step 2: Create a second product for comparison
            sample_products = self._create_sample_product_data()

            # Step 3: Use ComparisonEngine to compare products
            comparison_engine = ComparisonEngine()
            report = comparison_engine.compare_products(sample_products)

            # Verify comparison report
            self.assertIsNotNone(report)
            self.assertIn("Product Comparison:", report)
            self.assertIn("Comparison Matrix", report)
            self.assertIn("Feature Highlights", report)

            # Save report to temporary directory
            report_path = self.output_dir / "test_comparison_report.md"
            with open(report_path, "w") as f:
                f.write(report)

            print("✅ Data Processing to Comparison Engine integration test passed")
            print(f"   Report saved to {report_path}")
            return True

        except Exception as e:
            self.fail(f"Integration test failed: {e}")
            return False

    def test_web_scraping_to_data_processing_integration(self):
        """Test integration between web scraping and data processing."""
        print("\nTesting Web Scraping to Data Processing Integration...")

        try:
            # Step 1: Extract specifications using WebScrapingAdapter
            web_scraper = WebScrapingAdapter()
            raw_specs = web_scraper.extract_specifications(
                self.sample_html, self.product_url
            )

            # Verify raw specifications
            self.assertIsNotNone(raw_specs)
            self.assertIn("product_name", raw_specs)
            self.assertIn("specifications", raw_specs)
            self.assertIn("source_url", raw_specs)
            self.assertIn("source_domain", raw_specs)

            # Step 2: Process raw specifications using DataProcessor
            data_processor = DataProcessor()
            processed_data = data_processor.process_product_data(
                self.sample_html, self.product_url, self.product_category
            )

            # Verify processed data
            self.assertIsNotNone(processed_data)
            self.assertIn("normalized_specs", processed_data)
            self.assertIn("marketing_claims", processed_data)
            self.assertIn("raw_specs", processed_data)

            # Save processed data to temporary directory
            processed_data_path = self.output_dir / "test_processed_data.json"
            with open(processed_data_path, "w") as f:
                json.dump(processed_data, f, indent=2)

            print("✅ Web Scraping to Data Processing integration test passed")
            print(f"   Processed data saved to {processed_data_path}")
            return True

        except Exception as e:
            self.fail(f"Integration test failed: {e}")
            return False

    def test_crew_initialization(self):
        """Test crew initialization with product list."""
        print("\nTesting Crew Initialization...")

        try:
            # Skip this test if environment variables are not set
            if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("SERPER_API_KEY"):
                print("⚠️ Skipping crew initialization test: API keys not set")
                return True

            # Initialize crew with sample products
            products = ["Smartphone A", "Smartphone B"]
            crew = ProductResearchCrew(products)

            # Verify crew initialization
            self.assertIsNotNone(crew)
            self.assertEqual(crew.products, products)
            self.assertIsNotNone(crew.agents_config)
            self.assertIsNotNone(crew.tasks_config)
            self.assertIn("ScrapeWebsiteTool", crew.tools)
            self.assertIn("SerperDevTool", crew.tools)

            # Test agent creation
            for agent_name in crew.agents_config:
                agent = crew.create_agent(agent_name)
                self.assertIsNotNone(agent)
                self.assertEqual(
                    agent.role, crew.agents_config[agent_name].get("role", "")
                )

            print("✅ Crew initialization test passed")
            return True

        except Exception as e:
            self.fail(f"Crew initialization test failed: {e}")
            return False


def run_all_tests():
    """Run all integration tests."""
    print("Running Integration Tests for AI Product Research System...\n")

    # Run tests using unittest
    test_suite = main(module=__name__, exit=False)

    # Return success status
    return test_suite.result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
