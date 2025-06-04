"""
Data Processing Module for AI Product Research System

This module handles the data processing layer for the product research system:
1. Web scraping adapters for different sources
2. Specification extraction pipeline
3. Marketing claim detection
4. Data normalisation framework
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from error_handling import (
    DataProcessingError,
    ErrorHandler,
    ErrorSeverity,
    log_error,
)


class WebScrapingAdapter:
    """
    Adapter for web scraping that handles different website structures
    and extracts product specifications in a standardized format.
    """

    def __init__(self):
        self.site_adapters = {
            "amazon": self._extract_amazon,
            "bestbuy": self._extract_bestbuy,
            "newegg": self._extract_newegg,
            "techradar": self._extract_techradar,
            "cnet": self._extract_cnet,
            "gsmarena": self._extract_gsmarena,
            "default": self._extract_default,
        }

    def extract_specifications(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract product specifications from HTML content based on the source website.

        Args:
            html_content: The HTML content of the product page
            url: The URL of the product page

        Returns:
            Dictionary containing extracted product specifications
        """
        try:
            # Determine the website domain
            domain = self._get_domain(url)

            # Parse the HTML content
            soup = BeautifulSoup(html_content, "html.parser")

            # Use the appropriate adapter based on the domain
            adapter = self.site_adapters.get(domain, self.site_adapters["default"])

            # Extract specifications using the selected adapter
            specs = adapter(soup)

            # Add metadata
            specs["source_url"] = url
            specs["source_domain"] = domain

            return specs
        except Exception as e:
            error = DataProcessingError(
                f"Failed to extract specifications from {url}: {str(e)}",
                severity=ErrorSeverity.ERROR,
                details={"url": url, "domain": self._get_domain(url)},
            )
            log_error(error)
            raise error

    def _get_domain(self, url: str) -> str:
        """Extract the domain name from a URL."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Extract the main domain name (e.g., amazon from amazon.com)
        domain_parts = domain.split(".")
        if len(domain_parts) > 1:
            if domain_parts[0] == "www":
                return domain_parts[1].lower()
            return domain_parts[0].lower()

        return domain.lower()

    def _extract_amazon(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from Amazon product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one("#productTitle")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract price
        price_elem = soup.select_one("#priceblock_ourprice, .a-price .a-offscreen")
        if price_elem:
            specs["price"] = price_elem.text.strip()

        # Extract technical specifications
        tech_specs_table = soup.select_one(
            ".a-section.a-spacing-medium.a-spacing-top-small table"
        )
        if tech_specs_table:
            for row in tech_specs_table.select("tr"):
                cells = row.select("td, th")
                if len(cells) >= 2:
                    key = cells[0].text.strip().rstrip(":")
                    value = cells[1].text.strip()
                    specs["specifications"][key] = value

        return specs

    def _extract_bestbuy(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from Best Buy product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one(".sku-title h1")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract price
        price_elem = soup.select_one(".priceView-customer-price span")
        if price_elem:
            specs["price"] = price_elem.text.strip()

        # Extract technical specifications
        spec_groups = soup.select(".spec-group")
        for group in spec_groups:
            spec_header_elem = group.select_one(".spec-header")
            group_name = (
                spec_header_elem.text.strip() if spec_header_elem else "General"
            )
            specs["specifications"][group_name] = {}

            for item in group.select(".spec-list .spec-item"):
                key_elem = item.select_one(".spec-label")
                value_elem = item.select_one(".spec-value")

                if key_elem and value_elem:
                    key = key_elem.text.strip().rstrip(":")
                    value = value_elem.text.strip()
                    specs["specifications"][group_name][key] = value

        return specs

    def _extract_newegg(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from Newegg product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one(".product-title")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract price
        price_elem = soup.select_one(".price-current")
        if price_elem:
            specs["price"] = price_elem.text.strip()

        # Extract technical specifications
        spec_tables = soup.select("#Specs .table-horizontal")
        for table in spec_tables:
            for row in table.select("tr"):
                cells = row.select("th, td")
                if len(cells) >= 2:
                    key = cells[0].text.strip().rstrip(":")
                    value = cells[1].text.strip()
                    specs["specifications"][key] = value

        return specs

    def _extract_techradar(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from TechRadar product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one("h1.article-title")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract specifications from the article content
        spec_sections = soup.select(".specs-box")
        for section in spec_sections:
            section_title = section.select_one(".specs-box-title")
            section_name = section_title.text.strip() if section_title else "General"
            specs["specifications"][section_name] = {}

            for item in section.select(".specs-box-list li"):
                text = item.text.strip()
                if ":" in text:
                    key, value = text.split(":", 1)
                    specs["specifications"][section_name][key.strip()] = value.strip()

        return specs

    def _extract_cnet(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from CNET product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one("h1.specsHeader")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract specifications
        spec_tables = soup.select(".specTable")
        for table in spec_tables:
            section_title = table.select_one(".specTableHeader")
            section_name = section_title.text.strip() if section_title else "General"
            specs["specifications"][section_name] = {}

            for row in table.select("tr"):
                cells = row.select("td")
                if len(cells) >= 2:
                    key = cells[0].text.strip().rstrip(":")
                    value = cells[1].text.strip()
                    specs["specifications"][section_name][key] = value

        return specs

    def _extract_gsmarena(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications from GSMArena product pages."""
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Extract product name
        product_name_elem = soup.select_one("h1.specs-phone-name-title")
        if product_name_elem:
            specs["product_name"] = product_name_elem.text.strip()

        # Extract specifications
        spec_tables = soup.select(".specs-table-section")
        for table in spec_tables:
            section_title = table.select_one(".specs-table-subheading")
            section_name = section_title.text.strip() if section_title else "General"
            specs["specifications"][section_name] = {}

            for row in table.select("tr"):
                cells = row.select("td, th")
                if len(cells) >= 2:
                    key = cells[0].text.strip().rstrip(":")
                    value = cells[1].text.strip()
                    specs["specifications"][section_name][key] = value

        return specs

    def _extract_default(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Generic extraction method for websites without a specific adapter.
        Uses heuristics to find product specifications.
        """
        specs = {"product_name": "", "price": "", "specifications": {}}

        # Try to extract product name from common patterns
        product_name_candidates = [
            soup.select_one("h1"),
            soup.select_one(".product-title"),
            soup.select_one(".product-name"),
            soup.select_one("[itemprop='name']"),
        ]

        for candidate in product_name_candidates:
            if candidate and candidate.text.strip():
                specs["product_name"] = candidate.text.strip()
                break

        # Try to extract price from common patterns
        price_candidates = [
            soup.select_one(".price"),
            soup.select_one("[itemprop='price']"),
            soup.select_one(".product-price"),
        ]

        for candidate in price_candidates:
            if candidate and candidate.text.strip():
                specs["price"] = candidate.text.strip()
                break

        # Look for specification tables
        spec_tables = soup.select("table")
        for table in spec_tables:
            # Check if this looks like a specifications table
            if len(table.select("tr")) > 2:  # At least a few rows
                for row in table.select("tr"):
                    cells = row.select("td, th")
                    if len(cells) >= 2:
                        key = cells[0].text.strip().rstrip(":")
                        value = cells[1].text.strip()
                        if (
                            key and value
                        ):  # Only add if both key and value are non-empty
                            specs["specifications"][key] = value

        # Look for specification lists
        spec_lists = soup.select(
            "dl, ul.specs, ul.specifications, div.specs, div.specifications"
        )
        for spec_list in spec_lists:
            # For definition lists
            if spec_list.name == "dl":
                dt_elements = spec_list.select("dt")
                dd_elements = spec_list.select("dd")

                for i in range(min(len(dt_elements), len(dd_elements))):
                    key = dt_elements[i].text.strip().rstrip(":")
                    value = dd_elements[i].text.strip()
                    if key and value:
                        specs["specifications"][key] = value

            # For unordered lists
            elif spec_list.name == "ul":
                for item in spec_list.select("li"):
                    text = item.text.strip()
                    if ":" in text:
                        key, value = text.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            specs["specifications"][key] = value

        return specs


class SpecificationExtractor:
    """
    Extracts and structures product specifications from raw data.
    """

    def __init__(self):
        self.category_patterns = self._load_category_patterns()

    def _load_category_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load category-specific patterns for specification extraction."""
        # In a real implementation, this would load from a configuration file
        return {
            "smartphone": {
                "processor": [
                    r"processor",
                    r"cpu",
                    r"chipset",
                    r"soc",
                ],
                "memory": [
                    r"ram",
                    r"memory",
                    r"internal storage",
                ],
                "display": [
                    r"display",
                    r"screen",
                    r"resolution",
                ],
                "camera": [
                    r"camera",
                    r"rear camera",
                    r"front camera",
                ],
                "battery": [
                    r"battery",
                    r"capacity",
                ],
            },
            "laptop": {
                "processor": [
                    r"processor",
                    r"cpu",
                ],
                "memory": [
                    r"ram",
                    r"memory",
                ],
                "storage": [
                    r"storage",
                    r"ssd",
                    r"hdd",
                    r"hard drive",
                ],
                "display": [
                    r"display",
                    r"screen",
                    r"resolution",
                ],
                "graphics": [
                    r"graphics",
                    r"gpu",
                    r"video card",
                ],
            },
            # Add more product categories as needed
        }

    def extract_structured_specs(
        self, raw_specs: Dict[str, Any], product_category: str
    ) -> Dict[str, Any]:
        """
        Extract structured specifications from raw data based on product category.

        Args:
            raw_specs: Raw specifications extracted from web scraping
            product_category: Category of the product (e.g., smartphone, laptop)

        Returns:
            Dictionary with structured specifications
        """
        structured_specs = {
            "product_name": raw_specs.get("product_name", ""),
            "price": raw_specs.get("price", ""),
            "source_url": raw_specs.get("source_url", ""),
            "source_domain": raw_specs.get("source_domain", ""),
            "specifications": {},
        }

        # Get category patterns or use default
        category = product_category.lower()
        patterns = self.category_patterns.get(category)
        if patterns is None:
            patterns = self.category_patterns.get("smartphone", {})

        # Extract specifications based on patterns
        raw_spec_data = raw_specs.get("specifications", {})

        # Handle both flat and nested specifications
        flat_specs = {}
        if isinstance(raw_spec_data, dict):
            for key, value in raw_spec_data.items():
                if isinstance(value, dict):
                    # Handle nested specifications
                    for sub_key, sub_value in value.items():
                        flat_specs[f"{key} - {sub_key}"] = sub_value
                else:
                    flat_specs[key] = value

        # Categorize specifications
        for category_name, category_patterns in patterns.items():
            structured_specs["specifications"][category_name] = {}

            for key, value in flat_specs.items():
                for pattern in category_patterns:
                    if re.search(pattern, key, re.IGNORECASE):
                        structured_specs["specifications"][category_name][key] = value
                        break

        # Add uncategorized specifications
        structured_specs["specifications"]["other"] = {}
        for key, value in flat_specs.items():
            # Check if this key was already categorized
            categorized = False
            for category_name in patterns.keys():
                if key in structured_specs["specifications"].get(category_name, {}):
                    categorized = True
                    break

            if not categorized:
                structured_specs["specifications"]["other"][key] = value

        return structured_specs


class MarketingClaimDetector:
    """
    Detects and filters marketing claims from product specifications.
    """

    def __init__(self):
        self.marketing_phrases = self._load_marketing_phrases()
        self.superlative_patterns = [
            r"best",
            r"fastest",
            r"ultimate",
            r"premium",
            r"superior",
            r"excellent",
            r"outstanding",
            r"exceptional",
            r"revolutionary",
            r"groundbreaking",
            r"cutting-edge",
            r"state-of-the-art",
            r"next-generation",
            r"unparalleled",
            r"unmatched",
            r"unrivaled",
        ]

    def _load_marketing_phrases(self) -> List[str]:
        """Load common marketing phrases."""
        # In a real implementation, this would load from a configuration file
        return [
            "industry-leading",
            "game-changing",
            "revolutionary",
            "cutting-edge",
            "next-generation",
            "state-of-the-art",
            "best-in-class",
            "world-class",
            "premium",
            "professional-grade",
            "high-performance",
            "ultra",
            "super",
            "mega",
            "extreme",
            "enhanced",
            "advanced",
            "intelligent",
            "smart",
            "innovative",
            "breakthrough",
            "seamless",
            "immersive",
            "stunning",
            "beautiful",
            "sleek",
            "elegant",
            "powerful",
            "blazing-fast",
            "lightning-fast",
            "incredible",
            "amazing",
            "extraordinary",
            "exceptional",
            "outstanding",
            "superior",
            "excellent",
            "perfect",
            "flawless",
            "unbeatable",
            "unmatched",
            "unparalleled",
            "unrivaled",
            "unsurpassed",
        ]

    def detect_marketing_claims(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detect marketing claims in text.

        Args:
            text: Text to analyze

        Returns:
            Tuple containing:
            - Boolean indicating if marketing claims were detected
            - Confidence score (0-1)
            - List of detected marketing phrases
        """
        text_lower = text.lower()
        detected_phrases = []

        # Check for marketing phrases
        for phrase in self.marketing_phrases:
            if phrase.lower() in text_lower:
                detected_phrases.append(phrase)

        # Check for superlative patterns
        for pattern in self.superlative_patterns:
            matches = re.findall(r"\b" + pattern + r"\b", text_lower, re.IGNORECASE)
            detected_phrases.extend(matches)

        # Calculate confidence score based on number of detected phrases
        confidence = min(1.0, len(detected_phrases) / 3.0)  # Cap at 1.0

        return bool(detected_phrases), confidence, detected_phrases

    def filter_marketing_claims(
        self, specs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Filter marketing claims from product specifications.

        Args:
            specs: Product specifications

        Returns:
            Tuple containing:
            - Filtered specifications (factual)
            - Dictionary of detected marketing claims
        """
        filtered_specs = {
            "product_name": specs.get("product_name", ""),
            "price": specs.get("price", ""),
            "source_url": specs.get("source_url", ""),
            "source_domain": specs.get("source_domain", ""),
            "specifications": {},
        }

        marketing_claims = {
            "product_name": "",
            "claims": {},
        }

        # Check product name for marketing claims
        is_marketing, confidence, phrases = self.detect_marketing_claims(
            filtered_specs["product_name"]
        )
        if is_marketing:
            marketing_claims["product_name"] = {
                "text": filtered_specs["product_name"],
                "confidence": confidence,
                "phrases": phrases,
            }

        # Check specifications for marketing claims
        for category, category_specs in specs.get("specifications", {}).items():
            filtered_specs["specifications"][category] = {}
            marketing_claims["claims"][category] = {}

            for key, value in category_specs.items():
                if isinstance(value, str):
                    is_marketing, confidence, phrases = self.detect_marketing_claims(
                        value
                    )

                    # Always keep the specification, but mark it if it contains marketing claims
                    filtered_specs["specifications"][category][key] = value

                    if is_marketing:
                        marketing_claims["claims"][category][key] = {
                            "text": value,
                            "confidence": confidence,
                            "phrases": phrases,
                        }
                else:
                    # Non-string values are kept as-is
                    filtered_specs["specifications"][category][key] = value

        return filtered_specs, marketing_claims


class DataNormalizer:
    """
    Normalizes product specifications to ensure consistent units and formats.
    """

    def __init__(self):
        self.unit_patterns = {
            "storage": [
                (r"(\d+(?:\.\d+)?)\s*GB", self._convert_to_gb),
                (r"(\d+(?:\.\d+)?)\s*TB", self._convert_tb_to_gb),
                (r"(\d+(?:\.\d+)?)\s*MB", self._convert_mb_to_gb),
            ],
            "memory": [
                (r"(\d+(?:\.\d+)?)\s*GB", self._convert_to_gb),
                (r"(\d+(?:\.\d+)?)\s*MB", self._convert_mb_to_gb),
            ],
            "display": [
                (r"(\d+(?:\.\d+)?)\s*inch", self._convert_to_inch),
                (r'(\d+(?:\.\d+)?)"', self._convert_to_inch),
                (r"(\d+(?:\.\d+)?)\s*cm", self._convert_cm_to_inch),
                (r"(\d+)\s*x\s*(\d+)", self._format_resolution),
            ],
            "processor": [
                (r"(\d+(?:\.\d+)?)\s*GHz", self._convert_to_ghz),
                (r"(\d+(?:\.\d+)?)\s*MHz", self._convert_mhz_to_ghz),
            ],
            "battery": [
                (r"(\d+(?:\.\d+)?)\s*mAh", self._convert_to_mah),
                (r"(\d+(?:\.\d+)?)\s*Wh", self._convert_wh_to_mah),
            ],
            "weight": [
                (r"(\d+(?:\.\d+)?)\s*g", self._convert_to_g),
                (r"(\d+(?:\.\d+)?)\s*kg", self._convert_kg_to_g),
                (r"(\d+(?:\.\d+)?)\s*lbs", self._convert_lbs_to_g),
                (r"(\d+(?:\.\d+)?)\s*oz", self._convert_oz_to_g),
            ],
        }

    def _convert_to_gb(self, match):
        """Convert GB to GB (identity function)."""
        return f"{float(match.group(1)):.0f} GB"

    def _convert_tb_to_gb(self, match):
        """Convert TB to GB."""
        return f"{float(match.group(1)) * 1024:.0f} GB"

    def _convert_mb_to_gb(self, match):
        """Convert MB to GB."""
        return f"{float(match.group(1)) / 1024:.2f} GB"

    def _convert_to_inch(self, match):
        """Convert inch to inch (identity function)."""
        return f'{float(match.group(1)):.1f}"'

    def _convert_cm_to_inch(self, match):
        """Convert cm to inch."""
        return f'{float(match.group(1)) / 2.54:.1f}"'

    def _format_resolution(self, match):
        """Format resolution as WxH."""
        return f"{match.group(1)}x{match.group(2)}"

    def _convert_to_ghz(self, match):
        """Convert GHz to GHz (identity function)."""
        return f"{float(match.group(1)):.2f} GHz"

    def _convert_mhz_to_ghz(self, match):
        """Convert MHz to GHz."""
        return f"{float(match.group(1)) / 1000:.2f} GHz"

    def _convert_to_mah(self, match):
        """Convert mAh to mAh (identity function)."""
        return f"{float(match.group(1)):.0f} mAh"

    def _convert_wh_to_mah(self, match):
        """Convert Wh to mAh (approximate conversion)."""
        # Assuming 3.7V for Li-ion batteries
        return f"{float(match.group(1)) * 270:.0f} mAh"

    def _convert_to_g(self, match):
        """Convert g to g (identity function)."""
        return f"{float(match.group(1)):.0f} g"

    def _convert_kg_to_g(self, match):
        """Convert kg to g."""
        return f"{float(match.group(1)) * 1000:.0f} g"

    def _convert_lbs_to_g(self, match):
        """Convert lbs to g."""
        return f"{float(match.group(1)) * 453.592:.0f} g"

    def _convert_oz_to_g(self, match):
        """Convert oz to g."""
        return f"{float(match.group(1)) * 28.3495:.0f} g"

    def normalize_value(self, value: str, category: str, key: str) -> str:
        """
        Normalize a specification value based on category and key.

        Args:
            value: The value to normalize
            category: The specification category (e.g., storage, memory)
            key: The specification key

        Returns:
            Normalized value
        """
        if not isinstance(value, str):
            return value

        # Determine which category of patterns to use
        pattern_category = None
        for cat in self.unit_patterns.keys():
            if cat.lower() in category.lower() or cat.lower() in key.lower():
                pattern_category = cat
                break

        if not pattern_category:
            return value

        # Apply normalization patterns
        normalized_value = value
        for pattern, converter in self.unit_patterns[pattern_category]:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                normalized_value = converter(match)
                break

        return normalized_value

    def normalize_specifications(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all specifications in a product.

        Args:
            specs: Product specifications

        Returns:
            Normalized specifications
        """
        normalized_specs = {
            "product_name": specs.get("product_name", ""),
            "price": specs.get("price", ""),
            "source_url": specs.get("source_url", ""),
            "source_domain": specs.get("source_domain", ""),
            "specifications": {},
        }

        for category, category_specs in specs.get("specifications", {}).items():
            normalized_specs["specifications"][category] = {}

            for key, value in category_specs.items():
                normalized_value = self.normalize_value(value, category, key)
                normalized_specs["specifications"][category][key] = normalized_value

        return normalized_specs


class DataProcessor:
    """
    Main class that orchestrates the data processing pipeline.
    """

    def __init__(self):
        self.web_scraper = WebScrapingAdapter()
        self.spec_extractor = SpecificationExtractor()
        self.marketing_detector = MarketingClaimDetector()
        self.data_normalizer = DataNormalizer()

    def process_product_data(
        self, html_content: str, url: str, product_category: str
    ) -> Dict[str, Any]:
        """
        Process product data through the complete pipeline.

        Args:
            html_content: HTML content of the product page
            url: URL of the product page
            product_category: Category of the product

        Returns:
            Processed product data
        """
        with ErrorHandler(
            context={
                "url": url,
                "product_category": product_category,
                "operation": "process_product_data",
            }
        ) as handler:
            # Step 1: Extract raw specifications
            raw_specs = self.web_scraper.extract_specifications(html_content, url)

            # Step 2: Extract structured specifications
            structured_specs = self.spec_extractor.extract_structured_specs(
                raw_specs, product_category
            )

            # Step 3: Filter marketing claims
            factual_specs, marketing_claims = (
                self.marketing_detector.filter_marketing_claims(structured_specs)
            )

            # Step 4: Normalize specifications
            normalized_specs = self.data_normalizer.normalize_specifications(
                factual_specs
            )

            # Combine results
            result = {
                "normalized_specs": normalized_specs,
                "marketing_claims": marketing_claims,
                "raw_specs": raw_specs,
            }

            return result

        if handler.has_error:
            # Return a minimal result with error information
            return {
                "error": str(handler.error),
                "normalized_specs": {},
                "marketing_claims": {},
                "raw_specs": {},
            }

    def save_processed_data(self, data: Dict[str, Any], product_name: str) -> Path:
        """
        Save processed data to a file.

        Args:
            data: Processed product data
            product_name: Name of the product

        Returns:
            Path to the saved file
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("output/processed_data")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create a safe filename
            safe_name = re.sub(r"[^\w\-\.]", "_", product_name)
            file_path = output_dir / f"{safe_name}.json"

            # Save data to file
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)

            return file_path
        except Exception as e:
            error = DataProcessingError(
                f"Failed to save processed data for {product_name}: {str(e)}",
                severity=ErrorSeverity.ERROR,
                details={"product_name": product_name, "output_dir": str(output_dir)},
            )
            log_error(error)
            raise error


# Example usage
if __name__ == "__main__":
    # This would be used for testing the module
    processor = DataProcessor()

    print("Data Processing Module loaded successfully")
    print("Use DataProcessor class to process product data")
