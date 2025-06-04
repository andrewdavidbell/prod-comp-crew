"""
Example script demonstrating the use of the Comparison Engine.

This script creates sample product data and uses the ComparisonEngine
to generate a comparison report.
"""

import json
from datetime import datetime
from pathlib import Path

from comparison_engine import ComparisonEngine


def create_sample_product_data():
    """Create sample product data for demonstration."""
    return [
        {
            "product_name": "Laptop X",
            "price": "£1299.99",
            "source_url": "https://example.com/products/laptop-x",
            "source_domain": "example",
            "specifications": {
                "processor": {
                    "CPU": "Intel Core i7-12700H",
                    "Cores": "14 cores (6P + 8E)",
                    "Base Frequency": "2.3GHz",
                    "Turbo Frequency": "4.7GHz",
                },
                "memory": {
                    "RAM": "16GB DDR5",
                    "Storage": "512GB SSD",
                },
                "display": {
                    "Screen Size": "15.6 inch",
                    "Resolution": "2560x1440",
                    "Refresh Rate": "165Hz",
                    "Panel Type": "IPS",
                },
                "graphics": {
                    "GPU": "NVIDIA RTX 3070",
                    "VRAM": "8GB GDDR6",
                },
                "battery": {
                    "Capacity": "80Wh",
                    "Battery Life": "Up to 8 hours",
                },
                "connectivity": {
                    "Ports": "2x USB-C, 3x USB-A, HDMI, Ethernet",
                    "Wireless": "Wi-Fi 6E, Bluetooth 5.2",
                },
                "other": {
                    "Weight": "2.1 kg",
                    "Dimensions": "35.8 x 26.7 x 2.3 cm",
                    "Operating System": "Windows 11 Home",
                },
            },
        },
        {
            "product_name": "Laptop Y",
            "price": "£1499.99",
            "source_url": "https://example.com/products/laptop-y",
            "source_domain": "example",
            "specifications": {
                "processor": {
                    "Processor": "AMD Ryzen 9 6900HX",
                    "Core Count": "8 cores, 16 threads",
                    "Base Clock": "3.3GHz",
                    "Max Boost": "4.9GHz",
                },
                "memory": {
                    "Memory": "32GB DDR5",
                    "Storage Capacity": "1TB NVMe SSD",
                },
                "display": {
                    "Display": "16 inch",
                    "Screen Resolution": "3840x2400",
                    "Refresh": "240Hz",
                    "Display Type": "OLED",
                },
                "graphics": {
                    "Graphics Card": "NVIDIA RTX 3080",
                    "Video Memory": "16GB GDDR6",
                },
                "battery": {
                    "Battery Capacity": "90Wh",
                    "Runtime": "Up to 10 hours",
                },
                "connectivity": {
                    "Available Ports": "3x USB-C, 2x USB-A, HDMI, SD Card Reader",
                    "Wireless Connectivity": "Wi-Fi 6E, Bluetooth 5.3",
                },
                "other": {
                    "Weight": "2.3 kg",
                    "Physical Dimensions": "36.2 x 27.5 x 2.5 cm",
                    "OS": "Windows 11 Pro",
                },
            },
        },
        {
            "product_name": "Laptop Z",
            "price": "£999.99",
            "source_url": "https://example.com/products/laptop-z",
            "source_domain": "example",
            "specifications": {
                "processor": {
                    "CPU Model": "Intel Core i5-12500H",
                    "CPU Cores": "12 cores (4P + 8E)",
                    "Base Speed": "2.5GHz",
                    "Turbo Speed": "4.5GHz",
                },
                "memory": {
                    "RAM Memory": "8GB DDR4",
                    "Internal Storage": "256GB SSD",
                },
                "display": {
                    "Screen": "14 inch",
                    "Resolution": "1920x1080",
                    "Refresh Rate": "144Hz",
                    "Panel": "IPS",
                },
                "graphics": {
                    "Graphics": "NVIDIA RTX 3050",
                    "Graphics Memory": "4GB GDDR6",
                },
                "battery": {
                    "Battery": "65Wh",
                    "Battery Life": "Up to 6 hours",
                },
                "connectivity": {
                    "Connectivity": "2x USB-C, 2x USB-A, HDMI",
                    "Wireless": "Wi-Fi 6, Bluetooth 5.1",
                },
                "other": {
                    "Device Weight": "1.8 kg",
                    "Size": "32.5 x 22.9 x 1.9 cm",
                    "Operating System": "Windows 11 Home",
                },
            },
        },
    ]


def save_sample_data(data, filename="sample_product_data.json"):
    """Save sample data to a JSON file."""
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    return file_path


def main():
    """Main function to demonstrate the comparison engine."""
    print("Comparison Engine Example")
    print("========================\n")

    # Create sample product data
    print("Creating sample product data...")
    products_data = create_sample_product_data()

    # Save sample data to a file
    data_file = save_sample_data(products_data)
    print(f"Sample data saved to {data_file}\n")

    # Create an instance of ComparisonEngine
    print("Initializing Comparison Engine...")
    engine = ComparisonEngine()

    # Compare products
    print("Comparing products...")
    comparison_date = datetime.now().strftime("%Y-%m-%d")
    report = engine.compare_products(products_data, comparison_date)

    # Save the report
    report_file = engine.save_comparison_report(report, "laptop_comparison.md")
    print(f"Comparison report saved to {report_file}\n")

    # Print a preview of the report
    print("Report Preview:")
    print("---------------")
    preview_lines = report.split("\n")[:20]  # First 20 lines
    print("\n".join(preview_lines))
    print("...\n")

    print("Complete! Open the report file to view the full comparison.")


if __name__ == "__main__":
    main()
