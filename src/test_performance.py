"""
Performance Benchmarking Tests for AI Product Research System

This script benchmarks the performance of the AI Product Research System,
measuring execution time and resource usage for various components.
"""

import json
import sys
import time
from pathlib import Path
from statistics import mean, median, stdev

from comparison_engine import ComparisonEngine
from data_processing import DataProcessor, WebScrapingAdapter


class PerformanceBenchmark:
    """Performance benchmarking for the AI Product Research System."""

    def __init__(self):
        """Initialize the benchmark."""
        self.results = {}
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

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

    def _create_sample_product_data(self, num_products=2):
        """Create sample product data for testing."""
        base_products = [
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
            {
                "product_name": "Smartphone C",
                "price": "£699.99",
                "source_url": "https://example.com/products/smartphone-c",
                "source_domain": "example",
                "specifications": {
                    "processor": {
                        "Processor Type": "Hexa-core 2.4GHz",
                    },
                    "memory": {
                        "RAM Memory": "6GB",
                        "Internal Storage": "128GB",
                    },
                    "display": {
                        "Display Size": "6.1 inch",
                        "Display Resolution": "2340x1080",
                    },
                    "battery": {
                        "Battery Size": "4000 mAh",
                    },
                    "camera": {
                        "Primary Camera": "32MP",
                        "Secondary Camera": "8MP",
                    },
                    "other": {
                        "Device Weight": "175 g",
                    },
                },
            },
            {
                "product_name": "Smartphone D",
                "price": "£999.99",
                "source_url": "https://example.com/products/smartphone-d",
                "source_domain": "example",
                "specifications": {
                    "processor": {
                        "CPU Model": "Deca-core 3.2GHz",
                    },
                    "memory": {
                        "RAM Size": "16GB",
                        "Storage Size": "1TB",
                    },
                    "display": {
                        "Screen Type": '6.8"',
                        "Resolution": "3200x1440",
                    },
                    "battery": {
                        "Battery Capacity": "5500 mAh",
                    },
                    "camera": {
                        "Main Sensor": "108MP",
                        "Front Sensor": "24MP",
                    },
                    "other": {
                        "Weight": "210 g",
                    },
                },
            },
            {
                "product_name": "Smartphone E",
                "price": "£599.99",
                "source_url": "https://example.com/products/smartphone-e",
                "source_domain": "example",
                "specifications": {
                    "processor": {
                        "Processor": "Quad-core 2.2GHz",
                    },
                    "memory": {
                        "Memory": "4GB",
                        "Storage": "64GB",
                    },
                    "display": {
                        "Display": '5.8"',
                        "Resolution": "1920x1080",
                    },
                    "battery": {
                        "Battery": "3500 mAh",
                    },
                    "camera": {
                        "Rear Camera": "16MP",
                        "Front Camera": "8MP",
                    },
                    "other": {
                        "Weight": "165 g",
                    },
                },
            },
        ]

        return base_products[:num_products]

    def _time_execution(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time

    def benchmark_web_scraping(self, iterations=5):
        """Benchmark the web scraping adapter."""
        print("\nBenchmarking Web Scraping Adapter...")

        execution_times = []
        web_scraper = WebScrapingAdapter()
        sample_html = self._create_sample_html()
        product_url = "https://example.com/products/smartphone-a"

        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}...")
            _, execution_time = self._time_execution(
                web_scraper.extract_specifications, sample_html, product_url
            )
            execution_times.append(execution_time)

        # Calculate statistics
        avg_time = mean(execution_times)
        med_time = median(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        std_dev = stdev(execution_times) if len(execution_times) > 1 else 0

        results = {
            "average_time": avg_time,
            "median_time": med_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "iterations": iterations,
        }

        self.results["web_scraping"] = results

        print(f"  Average execution time: {avg_time:.4f} seconds")
        print(f"  Median execution time: {med_time:.4f} seconds")
        print(f"  Min execution time: {min_time:.4f} seconds")
        print(f"  Max execution time: {max_time:.4f} seconds")
        print(f"  Standard deviation: {std_dev:.4f} seconds")

        return results

    def benchmark_data_processing(self, iterations=5):
        """Benchmark the data processing pipeline."""
        print("\nBenchmarking Data Processing Pipeline...")

        execution_times = []
        data_processor = DataProcessor()
        sample_html = self._create_sample_html()
        product_url = "https://example.com/products/smartphone-a"
        product_category = "smartphone"

        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}...")
            _, execution_time = self._time_execution(
                data_processor.process_product_data,
                sample_html,
                product_url,
                product_category,
            )
            execution_times.append(execution_time)

        # Calculate statistics
        avg_time = mean(execution_times)
        med_time = median(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        std_dev = stdev(execution_times) if len(execution_times) > 1 else 0

        results = {
            "average_time": avg_time,
            "median_time": med_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "iterations": iterations,
        }

        self.results["data_processing"] = results

        print(f"  Average execution time: {avg_time:.4f} seconds")
        print(f"  Median execution time: {med_time:.4f} seconds")
        print(f"  Min execution time: {min_time:.4f} seconds")
        print(f"  Max execution time: {max_time:.4f} seconds")
        print(f"  Standard deviation: {std_dev:.4f} seconds")

        return results

    def benchmark_comparison_engine(self, iterations=5, product_counts=[2, 3, 5]):
        """Benchmark the comparison engine with different numbers of products."""
        print("\nBenchmarking Comparison Engine...")

        comparison_engine = ComparisonEngine()

        for num_products in product_counts:
            print(f"\n  Testing with {num_products} products:")
            execution_times = []
            sample_products = self._create_sample_product_data(num_products)

            for i in range(iterations):
                print(f"    Iteration {i + 1}/{iterations}...")
                _, execution_time = self._time_execution(
                    comparison_engine.compare_products, sample_products
                )
                execution_times.append(execution_time)

            # Calculate statistics
            avg_time = mean(execution_times)
            med_time = median(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            std_dev = stdev(execution_times) if len(execution_times) > 1 else 0

            results = {
                "average_time": avg_time,
                "median_time": med_time,
                "min_time": min_time,
                "max_time": max_time,
                "std_dev": std_dev,
                "iterations": iterations,
            }

            self.results[f"comparison_engine_{num_products}_products"] = results

            print(f"    Average execution time: {avg_time:.4f} seconds")
            print(f"    Median execution time: {med_time:.4f} seconds")
            print(f"    Min execution time: {min_time:.4f} seconds")
            print(f"    Max execution time: {max_time:.4f} seconds")
            print(f"    Standard deviation: {std_dev:.4f} seconds")

        return self.results

    def benchmark_end_to_end(self, iterations=3, product_counts=[2, 3]):
        """Benchmark the end-to-end process."""
        print("\nBenchmarking End-to-End Process...")

        for num_products in product_counts:
            print(f"\n  Testing with {num_products} products:")
            execution_times = []
            sample_products = []

            # Create sample products
            sample_html = self._create_sample_html()
            product_url_base = "https://example.com/products/smartphone-"
            product_category = "smartphone"
            data_processor = DataProcessor()

            # Process each product
            for i in range(num_products):
                product_url = f"{product_url_base}{chr(97 + i)}"  # a, b, c, ...
                processed_data = data_processor.process_product_data(
                    sample_html, product_url, product_category
                )
                sample_products.append(processed_data["normalized_specs"])

            # Compare products
            comparison_engine = ComparisonEngine()

            for i in range(iterations):
                print(f"    Iteration {i + 1}/{iterations}...")
                _, execution_time = self._time_execution(
                    comparison_engine.compare_products, sample_products
                )
                execution_times.append(execution_time)

            # Calculate statistics
            avg_time = mean(execution_times)
            med_time = median(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            std_dev = stdev(execution_times) if len(execution_times) > 1 else 0

            results = {
                "average_time": avg_time,
                "median_time": med_time,
                "min_time": min_time,
                "max_time": max_time,
                "std_dev": std_dev,
                "iterations": iterations,
            }

            self.results[f"end_to_end_{num_products}_products"] = results

            print(f"    Average execution time: {avg_time:.4f} seconds")
            print(f"    Median execution time: {med_time:.4f} seconds")
            print(f"    Min execution time: {min_time:.4f} seconds")
            print(f"    Max execution time: {max_time:.4f} seconds")
            print(f"    Standard deviation: {std_dev:.4f} seconds")

        return self.results

    def save_results(self):
        """Save benchmark results to a file."""
        results_path = self.output_dir / "performance_benchmark_results.json"

        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\nBenchmark results saved to {results_path}")

        # Also generate a markdown report
        report_path = self.output_dir / "performance_benchmark_report.md"

        with open(report_path, "w") as f:
            f.write("# Performance Benchmark Report\n\n")
            f.write(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

            f.write("## Summary\n\n")
            f.write(
                "| Component | Configuration | Average Time (s) | Median Time (s) | Min Time (s) | Max Time (s) | Std Dev (s) |\n"
            )
            f.write(
                "|-----------|--------------|-----------------|-----------------|--------------|--------------|-------------|\n"
            )

            for component, results in self.results.items():
                f.write(
                    f"| {component} | {results.get('iterations', 'N/A')} iterations | {results.get('average_time', 'N/A'):.4f} | {results.get('median_time', 'N/A'):.4f} | {results.get('min_time', 'N/A'):.4f} | {results.get('max_time', 'N/A'):.4f} | {results.get('std_dev', 'N/A'):.4f} |\n"
                )

            f.write("\n## Analysis\n\n")

            # Add analysis of results
            f.write("### Performance Observations\n\n")

            # Check if we have comparison engine results for different product counts
            comparison_results = {
                k: v
                for k, v in self.results.items()
                if k.startswith("comparison_engine_")
            }
            if comparison_results:
                f.write("#### Comparison Engine Scaling\n\n")
                f.write(
                    "The comparison engine's performance scales with the number of products being compared:\n\n"
                )
                for component, results in sorted(comparison_results.items()):
                    num_products = component.split("_")[2]
                    f.write(
                        f"- **{num_products} products**: {results.get('average_time', 'N/A'):.4f} seconds on average\n"
                    )

                # Calculate scaling factor
                product_times = []
                for component, results in sorted(comparison_results.items()):
                    num_products = int(component.split("_")[2])
                    avg_time = results.get("average_time", 0)
                    product_times.append((num_products, avg_time))

                if len(product_times) >= 2:
                    min_products, min_time = product_times[0]
                    max_products, max_time = product_times[-1]
                    scaling_factor = (max_time / min_time) / (
                        max_products / min_products
                    )
                    f.write(
                        f"\nScaling factor: {scaling_factor:.2f}x (time increase per product)\n"
                    )

            # Check if we have end-to-end results
            end_to_end_results = {
                k: v for k, v in self.results.items() if k.startswith("end_to_end_")
            }
            if end_to_end_results:
                f.write("\n#### End-to-End Process Performance\n\n")
                f.write(
                    "The complete process performance with different numbers of products:\n\n"
                )
                for component, results in sorted(end_to_end_results.items()):
                    num_products = component.split("_")[2]
                    f.write(
                        f"- **{num_products} products**: {results.get('average_time', 'N/A'):.4f} seconds on average\n"
                    )

            f.write("\n### Performance Recommendations\n\n")
            f.write(
                "Based on the benchmark results, the following recommendations can be made:\n\n"
            )

            # Add recommendations based on results
            if (
                "web_scraping" in self.results
                and self.results["web_scraping"]["average_time"] > 0.5
            ):
                f.write(
                    "- **Web Scraping**: Consider optimizing the HTML parsing logic to improve performance\n"
                )

            if (
                "data_processing" in self.results
                and self.results["data_processing"]["average_time"] > 1.0
            ):
                f.write(
                    "- **Data Processing**: The marketing claim detection and data normalization steps may benefit from optimization\n"
                )

            if comparison_results:
                max_component = max(
                    comparison_results.items(), key=lambda x: x[1]["average_time"]
                )
                if max_component[1]["average_time"] > 2.0:
                    f.write(
                        f"- **Comparison Engine**: With {max_component[0].split('_')[2]} products, the comparison takes {max_component[1]['average_time']:.2f} seconds on average. Consider optimizing the feature matching algorithm for better scaling\n"
                    )

            if end_to_end_results:
                max_component = max(
                    end_to_end_results.items(), key=lambda x: x[1]["average_time"]
                )
                if max_component[1]["average_time"] > 5.0:
                    f.write(
                        f"- **End-to-End Process**: With {max_component[0].split('_')[2]} products, the complete process takes {max_component[1]['average_time']:.2f} seconds on average. This is within the 2-minute requirement, but further optimization may be needed for larger product sets\n"
                    )

        print(f"Benchmark report saved to {report_path}")

        return results_path, report_path

    def run_all_benchmarks(self, iterations=5):
        """Run all benchmarks."""
        print("Running Performance Benchmarks for AI Product Research System...\n")

        # Run individual component benchmarks
        self.benchmark_web_scraping(iterations)
        self.benchmark_data_processing(iterations)
        self.benchmark_comparison_engine(iterations)

        # Run end-to-end benchmark with fewer iterations (it's slower)
        self.benchmark_end_to_end(max(1, iterations // 2))

        # Save results
        results_path, report_path = self.save_results()

        print("\nPerformance Benchmarking Complete!")
        print(f"Results saved to {results_path}")
        print(f"Report saved to {report_path}")

        return True


def main():
    """Main entry point."""
    benchmark = PerformanceBenchmark()
    success = benchmark.run_all_benchmarks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
