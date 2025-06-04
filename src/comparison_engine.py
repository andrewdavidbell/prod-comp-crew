"""
Comparison Engine Module for AI Product Research System

This module implements the comparison engine for the product research system:
1. Feature matching algorithm
2. Dynamic markdown templating
3. Matrix generation logic
4. Unit conversion system
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from error_handling import (
    DataProcessingError,
    ErrorSeverity,
    log_error,
)


class FeatureMatcher:
    """
    Matches features across different products for accurate comparison.
    """

    def __init__(self):
        self.similarity_threshold = 0.7
        self.feature_categories = {
            "processor": ["processor", "cpu", "chipset", "soc"],
            "memory": ["ram", "memory"],
            "storage": ["storage", "disk", "drive", "ssd", "hdd"],
            "display": ["display", "screen", "monitor"],
            "camera": ["camera", "lens", "photo"],
            "battery": ["battery", "power", "charge"],
            "dimensions": ["dimensions", "size", "weight"],
            "connectivity": ["wifi", "bluetooth", "nfc", "usb", "port"],
            "os": ["os", "operating system", "software"],
            "price": ["price", "cost", "msrp"],
            "graphics": ["graphics", "gpu", "vga", "video"],
        }
        self.key_feature_patterns = self._compile_key_feature_patterns()

    def _compile_key_feature_patterns(self) -> Dict[str, Dict[str, re.Pattern]]:
        """Compile regex patterns for key features in each category."""
        patterns = {}
        for category, keywords in self.feature_categories.items():
            patterns[category] = {}
            for keyword in keywords:
                # Create pattern that matches the keyword as a whole word or part of a word
                patterns[category][keyword] = re.compile(
                    r"(?i)\b" + re.escape(keyword) + r"\w*\b"
                )
        return patterns

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity using a simple algorithm.
        Returns a value between 0 (no similarity) and 1 (identical).
        """
        # Convert to lowercase for case-insensitive comparison
        str1 = str1.lower()
        str2 = str2.lower()

        # If strings are identical, return 1.0
        if str1 == str2:
            return 1.0

        # Check for exact keyword matches (e.g., "RAM" in "RAM Memory")
        if str1 in str2 or str2 in str1:
            # If one is a substring of the other, consider them highly similar
            return 0.9

        # Calculate Jaccard similarity on words
        words1 = set(re.findall(r"\b\w+\b", str1))
        words2 = set(re.findall(r"\b\w+\b", str2))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _categorize_feature(self, feature_key: str) -> str:
        """Categorize a feature key based on keywords."""
        # Check if the feature key already includes a category (e.g., "memory - Storage")
        if " - " in feature_key:
            category, _ = feature_key.split(" - ", 1)
            return category.lower()

        feature_key_lower = feature_key.lower()

        # Check each category's patterns
        for category, patterns in self.key_feature_patterns.items():
            for keyword, pattern in patterns.items():
                if pattern.search(feature_key_lower):
                    return category

        # Default category if no match is found
        return "other"

    def _find_matching_feature(
        self, feature_key: str, target_features: Dict[str, Any]
    ) -> Optional[str]:
        """
        Find the best matching feature in target_features for the given feature_key.
        Returns the matching key or None if no good match is found.
        """
        best_match = None
        best_similarity = 0.0

        for target_key in target_features:
            similarity = self._calculate_similarity(feature_key, target_key)
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = target_key

        return best_match

    def match_features(
        self, products_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, List[Tuple[str, Any]]]]:
        """
        Match features across different products.

        Args:
            products_data: List of product data dictionaries

        Returns:
            Dictionary with matched features organized by category
        """
        if not products_data:
            return {}

        # Extract all features from all products
        all_features = {}
        for product_idx, product_data in enumerate(products_data):
            product_name = product_data.get(
                "product_name", f"Product {product_idx + 1}"
            )
            specs = product_data.get("specifications", {})

            # Flatten nested specifications
            flat_specs = {}
            for category, category_specs in specs.items():
                for key, value in category_specs.items():
                    flat_key = f"{category} - {key}" if category != "other" else key
                    flat_specs[flat_key] = value

            all_features[product_name] = flat_specs

        # Organize features by category
        categorized_features = {}
        for product_name, features in all_features.items():
            for feature_key, feature_value in features.items():
                category = self._categorize_feature(feature_key)

                if category not in categorized_features:
                    categorized_features[category] = {}

                if feature_key not in categorized_features[category]:
                    categorized_features[category][feature_key] = []

                categorized_features[category][feature_key].append(
                    (product_name, feature_value)
                )

        # Match similar features within each category
        matched_features = {}

        # Initialize all expected categories, including "other"
        expected_categories = list(self.feature_categories.keys()) + ["other"]
        for category in expected_categories:
            matched_features[category] = {}

        # Process features by category
        for category, features in categorized_features.items():
            # Process each feature
            processed_keys = set()
            for feature_key, product_values in features.items():
                if feature_key in processed_keys:
                    continue

                # Find similar features and merge them
                similar_features = [feature_key]
                for other_key in features:
                    if (
                        other_key != feature_key
                        and other_key not in processed_keys
                        and self._calculate_similarity(feature_key, other_key)
                        >= self.similarity_threshold
                    ):
                        similar_features.append(other_key)
                        processed_keys.add(other_key)

                # Use the most common feature key as the canonical key
                canonical_key = max(
                    similar_features, key=lambda k: len(features.get(k, []))
                )
                processed_keys.add(canonical_key)

                # Merge product values from all similar features
                merged_values = []
                for key in similar_features:
                    merged_values.extend(features.get(key, []))

                # Organize by product
                product_dict = {}
                for product_name, value in merged_values:
                    if product_name not in product_dict:
                        product_dict[product_name] = []
                    product_dict[product_name].append(value)

                # Use the first value if multiple values exist for a product
                final_values = []
                for product_name, values in product_dict.items():
                    final_values.append((product_name, values[0]))

                matched_features[category][canonical_key] = final_values

        return matched_features


class UnitConverter:
    """
    Handles unit conversions for proper comparisons.
    """

    def __init__(self):
        # Define conversion factors for different units
        self.conversion_factors = {
            "storage": {
                "KB": 1 / (1024 * 1024),  # KB to GB
                "MB": 1 / 1024,  # MB to GB
                "GB": 1.0,  # GB to GB (base unit)
                "TB": 1024.0,  # TB to GB
            },
            "memory": {
                "MB": 1 / 1024,  # MB to GB
                "GB": 1.0,  # GB to GB (base unit)
            },
            "display": {
                "cm": 1 / 2.54,  # cm to inches
                "mm": 1 / 25.4,  # mm to inches
                "inch": 1.0,  # inch to inch (base unit)
                '"': 1.0,  # inch to inch (base unit)
            },
            "processor": {
                "MHz": 1 / 1000,  # MHz to GHz
                "GHz": 1.0,  # GHz to GHz (base unit)
            },
            "battery": {
                "mAh": 1.0,  # mAh to mAh (base unit)
                "Wh": 270.0,  # Wh to mAh (approximate, assuming 3.7V)
            },
            "weight": {
                "mg": 1 / 1000,  # mg to g
                "g": 1.0,  # g to g (base unit)
                "kg": 1000.0,  # kg to g
                "oz": 28.35,  # oz to g
                "lb": 453.59,  # lb to g
            },
        }

        # Define base units for each category
        self.base_units = {
            "storage": "GB",
            "memory": "GB",
            "display": "inch",
            "processor": "GHz",
            "battery": "mAh",
            "weight": "g",
            "resolution": "pixels",
            "refresh_rate": "Hz",
        }

        # Compile regex patterns for extracting values and units
        self.value_unit_patterns = {
            category: re.compile(
                r"(\d+(?:\.\d+)?)\s*(" + "|".join(map(re.escape, units.keys())) + r")"
            )
            for category, units in self.conversion_factors.items()
        }

    def extract_value_and_unit(
        self, value_str: str, category: str
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract numeric value and unit from a string.

        Args:
            value_str: String containing value and unit
            category: Category for determining the pattern to use

        Returns:
            Tuple of (numeric value, unit) or (None, None) if extraction fails
        """
        if not isinstance(value_str, str):
            return None, None

        # Use the appropriate pattern for the category
        pattern = self.value_unit_patterns.get(category)
        if not pattern:
            # Try a generic pattern if no category-specific pattern exists
            match = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", value_str)
            if match:
                return float(match.group(1)), match.group(2)
            return None, None

        match = pattern.search(value_str)
        if match:
            return float(match.group(1)), match.group(2)

        # Try a generic numeric extraction if the pattern doesn't match
        match = re.search(r"(\d+(?:\.\d+)?)", value_str)
        if match:
            return float(match.group(1)), None

        return None, None

    def convert_to_base_unit(
        self, value: float, unit: str, category: str
    ) -> Tuple[float, str]:
        """
        Convert a value to the base unit for its category.

        Args:
            value: Numeric value
            unit: Current unit
            category: Category for determining conversion factors

        Returns:
            Tuple of (converted value, base unit)
        """
        if (
            category not in self.conversion_factors
            or unit not in self.conversion_factors[category]
        ):
            return value, unit

        base_unit = self.base_units.get(category, unit)
        conversion_factor = self.conversion_factors[category][unit]
        converted_value = value * conversion_factor

        return converted_value, base_unit

    def normalize_for_comparison(
        self, value_str: str, category: str
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Normalize a value for comparison by converting to the base unit.

        Args:
            value_str: String containing value and unit
            category: Category for determining conversion factors

        Returns:
            Tuple of (normalized value, base unit) or (None, None) if normalization fails
        """
        value, unit = self.extract_value_and_unit(value_str, category)
        if value is None:
            return None, None

        if unit is None:
            # If no unit was found, use the base unit for the category
            return value, self.base_units.get(category, "")

        return self.convert_to_base_unit(value, unit, category)

    def is_comparable(self, value1: str, value2: str, category: str) -> bool:
        """
        Check if two values are comparable (have compatible units).

        Args:
            value1: First value string
            value2: Second value string
            category: Category for determining conversion factors

        Returns:
            Boolean indicating if values are comparable
        """
        norm1 = self.normalize_for_comparison(value1, category)
        norm2 = self.normalize_for_comparison(value2, category)

        return norm1[0] is not None and norm2[0] is not None

    def compare_values(
        self, value1: str, value2: str, category: str
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Compare two values by normalizing them to the same unit.

        Args:
            value1: First value string
            value2: Second value string
            category: Category for determining conversion factors

        Returns:
            Tuple of (normalized value1, normalized value2, base unit)
            or (None, None, None) if comparison fails
        """
        norm1 = self.normalize_for_comparison(value1, category)
        norm2 = self.normalize_for_comparison(value2, category)

        if norm1[0] is None or norm2[0] is None:
            return None, None, None

        return norm1[0], norm2[0], norm1[1]


class MatrixGenerator:
    """
    Generates comparison matrices for product features.
    """

    def __init__(self, unit_converter: Optional[UnitConverter] = None):
        self.unit_converter = unit_converter or UnitConverter()

    def generate_feature_matrix(
        self, matched_features: Dict[str, Dict[str, List[Tuple[str, Any]]]]
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Generate a feature comparison matrix.

        Args:
            matched_features: Dictionary with matched features organized by category

        Returns:
            Dictionary with feature matrix organized by category and feature
        """
        matrix = {}

        for category, features in matched_features.items():
            matrix[category] = {}

            for feature_key, product_values in features.items():
                matrix[category][feature_key] = {}

                # Extract all product names
                product_names = [product for product, _ in product_values]

                # Create a dictionary mapping product names to values
                for product_name, value in product_values:
                    matrix[category][feature_key][product_name] = value

                # Add comparison data if applicable
                if (
                    len(product_values) > 1
                    and category in self.unit_converter.base_units
                ):
                    # Try to normalize and compare values
                    comparable_values = []
                    for product_name, value in product_values:
                        if isinstance(value, str):
                            norm_value, unit = (
                                self.unit_converter.normalize_for_comparison(
                                    value, category
                                )
                            )
                            if norm_value is not None:
                                comparable_values.append(
                                    (product_name, norm_value, unit)
                                )

                    if len(comparable_values) > 1:
                        # Find the best (highest or lowest) value depending on category
                        if category in [
                            "processor",
                            "memory",
                            "storage",
                            "display",
                            "graphics",
                        ]:
                            # Higher is better
                            best_product = max(comparable_values, key=lambda x: x[1])
                            comparison_type = "higher_better"
                        elif category in ["weight"]:
                            # Lower is better
                            best_product = min(comparable_values, key=lambda x: x[1])
                            comparison_type = "lower_better"
                        else:
                            # No clear better/worse
                            best_product = None
                            comparison_type = "neutral"

                        # Special handling for resolution and refresh rate
                        if "resolution" in feature_key.lower():
                            best_product = max(comparable_values, key=lambda x: x[1])
                            comparison_type = "higher_better"
                            unit = "pixels"
                        elif (
                            "refresh" in feature_key.lower()
                            and "rate" in feature_key.lower()
                        ):
                            best_product = max(comparable_values, key=lambda x: x[1])
                            comparison_type = "higher_better"
                            unit = "Hz"

                        # Add comparison data
                        if best_product:
                            matrix[category][feature_key]["_comparison"] = {
                                "type": comparison_type,
                                "best_product": best_product[0],
                                "normalized_values": {
                                    p: v for p, v, _ in comparable_values
                                },
                                "unit": best_product[2],
                            }

        return matrix

    def generate_markdown_table(
        self, feature_matrix: Dict[str, Dict[str, Dict[str, Any]]], products: List[str]
    ) -> str:
        """
        Generate a markdown table from the feature matrix.

        Args:
            feature_matrix: Dictionary with feature matrix
            products: List of product names

        Returns:
            Markdown table as a string
        """
        if not feature_matrix or not products:
            return "No comparison data available."

        markdown = []

        # Generate tables for each category
        for category, features in feature_matrix.items():
            if not features:
                continue

            # Add category header
            markdown.append(f"### {category.title()}")
            markdown.append("")

            # Create table header
            header = ["Feature"] + products
            markdown.append("| " + " | ".join(header) + " |")
            markdown.append("| " + " | ".join(["---"] * len(header)) + " |")

            # Add rows for each feature
            for feature_key, product_values in features.items():
                row = [feature_key]

                for product in products:
                    value = product_values.get(product, "N/A")

                    # Check if this is the best value
                    if "_comparison" in product_values:
                        comparison = product_values["_comparison"]
                        if comparison["best_product"] == product:
                            value = f"**{value}**"  # Bold the best value

                    row.append(value)

                markdown.append("| " + " | ".join(row) + " |")

            markdown.append("")

        return "\n".join(markdown)


class MarkdownTemplateGenerator:
    """
    Generates dynamic markdown templates for comparison reports.
    """

    def __init__(self):
        self.template_sections = {
            "header": self._generate_header,
            "introduction": self._generate_introduction,
            "methodology": self._generate_methodology,
            "comparison_matrix": self._generate_comparison_matrix,
            "feature_highlights": self._generate_feature_highlights,
            "conclusion": self._generate_conclusion,
        }

    def _generate_header(self, products: List[str], comparison_date: str = "") -> str:
        """Generate the report header."""
        product_list = ", ".join(products)
        header = [
            f"# Product Comparison: {product_list}",
            "",
            f"*Comparison Date: {comparison_date}*",
            "",
            "---",
            "",
        ]
        return "\n".join(header)

    def _generate_introduction(self, products: List[str]) -> str:
        """Generate the introduction section."""
        product_count = len(products)
        product_list = ", ".join(products)

        intro = [
            "## Introduction",
            "",
            f"This report provides an objective technical comparison of {product_count} products: {product_list}. ",
            "The comparison is based on verified specifications from multiple sources, with marketing claims filtered out to ensure objectivity.",
            "",
        ]
        return "\n".join(intro)

    def _generate_methodology(self) -> str:
        """Generate the methodology section."""
        methodology = [
            "## Methodology",
            "",
            "This comparison was generated using an AI-powered product research system that:",
            "",
            "1. Collects product specifications from multiple authoritative sources",
            "2. Validates technical specifications against industry standards",
            "3. Filters out marketing language to focus on factual data",
            "4. Normalizes units and formats for accurate comparison",
            "5. Generates standardized comparison matrices",
            "",
            "All data has been processed to ensure accuracy and objectivity.",
            "",
        ]
        return "\n".join(methodology)

    def _generate_comparison_matrix(
        self,
        matrix_generator: MatrixGenerator,
        feature_matrix: Dict,
        products: List[str],
    ) -> str:
        """Generate the comparison matrix section."""
        matrix_md = [
            "## Comparison Matrix",
            "",
            "The following tables compare key features across all products:",
            "",
        ]

        # Add the actual matrix
        matrix_content = matrix_generator.generate_markdown_table(
            feature_matrix, products
        )
        matrix_md.append(matrix_content)

        return "\n".join(matrix_md)

    def _generate_feature_highlights(
        self, feature_matrix: Dict[str, Dict[str, Dict[str, Any]]]
    ) -> str:
        """Generate feature highlights section based on comparisons."""
        highlights = [
            "## Feature Highlights",
            "",
        ]

        # Extract highlights from the feature matrix
        highlight_points = []

        for category, features in feature_matrix.items():
            for feature_key, product_values in features.items():
                if "_comparison" in product_values:
                    comparison = product_values["_comparison"]
                    best_product = comparison["best_product"]
                    comparison_type = comparison["type"]
                    unit = comparison.get("unit", "")

                    if comparison_type == "higher_better":
                        highlight_points.append(
                            f"- **{best_product}** has the highest {feature_key.lower()} ({unit})"
                        )
                    elif comparison_type == "lower_better":
                        highlight_points.append(
                            f"- **{best_product}** has the lowest {feature_key.lower()} ({unit})"
                        )

        if highlight_points:
            highlights.extend(highlight_points)
        else:
            highlights.append("No specific highlights identified in the comparison.")

        highlights.append("")
        return "\n".join(highlights)

    def _generate_conclusion(self) -> str:
        """Generate the conclusion section."""
        conclusion = [
            "## Conclusion",
            "",
            "This comparison provides an objective overview of the technical specifications for the compared products. ",
            "The data presented is factual and free from marketing claims, allowing for an unbiased assessment of each product's capabilities.",
            "",
            "For specific use cases, consider which features are most important for your needs when making a decision.",
            "",
        ]
        return "\n".join(conclusion)

    def generate_template(
        self,
        products: List[str],
        feature_matrix: Dict[str, Dict[str, Dict[str, Any]]],
        comparison_date: str = "",
        sections: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a complete markdown template for the comparison report.

        Args:
            products: List of product names
            feature_matrix: Dictionary with feature matrix
            comparison_date: Date of the comparison
            sections: List of sections to include (defaults to all)

        Returns:
            Complete markdown template as a string
        """
        if sections is None:
            sections = list(self.template_sections.keys())

        markdown = []
        matrix_generator = MatrixGenerator()

        for section in sections:
            if section not in self.template_sections:
                continue

            if section == "comparison_matrix":
                section_content = self._generate_comparison_matrix(
                    matrix_generator, feature_matrix, products
                )
            elif section == "header":
                section_content = self._generate_header(products, comparison_date)
            elif section == "introduction":
                section_content = self._generate_introduction(products)
            elif section == "feature_highlights":
                section_content = self._generate_feature_highlights(feature_matrix)
            elif section == "conclusion":
                section_content = self._generate_conclusion()
            else:
                section_content = self.template_sections[section]()

            markdown.append(section_content)

        return "\n".join(markdown)


class ComparisonEngine:
    """
    Main class that orchestrates the comparison engine.
    """

    def __init__(self):
        self.feature_matcher = FeatureMatcher()
        self.unit_converter = UnitConverter()
        self.matrix_generator = MatrixGenerator(self.unit_converter)
        self.template_generator = MarkdownTemplateGenerator()

    def compare_products(
        self, products_data: List[Dict[str, Any]], comparison_date: str = ""
    ) -> str:
        """
        Compare products and generate a comparison report.

        Args:
            products_data: List of product data dictionaries
            comparison_date: Date of the comparison

        Returns:
            Markdown comparison report
        """
        try:
            # Extract product names
            product_names = [
                data.get("product_name", f"Product {i + 1}")
                for i, data in enumerate(products_data)
            ]

            # Match features across products
            matched_features = self.feature_matcher.match_features(products_data)

            # Generate feature matrix
            feature_matrix = self.matrix_generator.generate_feature_matrix(
                matched_features
            )

            # Generate markdown template
            markdown_report = self.template_generator.generate_template(
                product_names, feature_matrix, comparison_date
            )

            return markdown_report
        except Exception as e:
            error = DataProcessingError(
                f"Failed to compare products: {str(e)}",
                severity=ErrorSeverity.ERROR,
                details={"product_count": len(products_data)},
            )
            log_error(error)
            raise error

    def save_comparison_report(
        self, report: str, filename: str = "comparison_report.md"
    ) -> Path:
        """
        Save the comparison report to a file.

        Args:
            report: Markdown comparison report
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save report to file
            file_path = output_dir / filename
            with open(file_path, "w") as f:
                f.write(report)

            return file_path
        except Exception as e:
            error = DataProcessingError(
                f"Failed to save comparison report: {str(e)}",
                severity=ErrorSeverity.ERROR,
                details={"filename": filename, "output_dir": str(output_dir)},
            )
            log_error(error)
            raise error


# Example usage
if __name__ == "__main__":
    # This would be used for testing the module
    engine = ComparisonEngine()

    print("Comparison Engine Module loaded successfully")
    print("Use ComparisonEngine class to compare products")
