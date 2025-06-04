# AI Product Research System - User Documentation

## Overview

The AI Product Research System is a powerful tool designed to automate product research using collaborative AI agents. It generates objective technical comparisons from diverse sources and outputs standardised markdown reports with feature matrices.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys for:
  - OpenRouter (for LLM access)
  - Serper (for web search capabilities)

### Standard Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-product-research.git
   cd ai-product-research
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENROUTER_API_KEY=your_openrouter_key
     SERPER_API_KEY=your_serper_key
     ```

### Docker Installation

The system includes Docker containerization for easy deployment and cross-platform compatibility:

1. Build the Docker image:
   ```bash
   docker build -t ai-product-research .
   ```

2. Run the container with environment variables:
   ```bash
   docker run -e OPENROUTER_API_KEY=your_key -e SERPER_API_KEY=your_key ai-product-research
   ```

3. Using docker-compose (recommended):
   ```bash
   # Edit the .env file first with your API keys
   docker-compose up
   ```

#### Docker Compose Configuration

The `docker-compose.yml` file provides a complete deployment configuration:

```yaml
services:
  ai-product-research:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    env_file:
      - .env
    ports:
      - "8080:8080"
```

This configuration:
- Mounts the output and logs directories for persistent storage
- Uses the .env file for environment variables
- Exposes port 8080 for web interface access (if enabled)

#### Container Management

- View logs: `docker-compose logs`
- Stop the container: `docker-compose down`
- Rebuild after changes: `docker-compose up --build`

## Configuration

The system is configuration-driven using YAML files located in the `config/` directory:

### Agent Configuration (`config/agents.yaml`)

This file defines the AI agents used in the system:

```yaml
agents:
  researcher:
    name: "Research Agent"
    role: "Product Researcher"
    goal: "Find accurate technical specifications for products"
    backstory: "Expert at gathering technical data from diverse sources"
    tools: ["web_search", "data_extraction"]

  analyst:
    name: "Analysis Agent"
    role: "Data Analyst"
    goal: "Validate and normalise technical specifications"
    backstory: "Specialist in data validation and standardisation"
    tools: ["data_validation", "unit_conversion"]

  comparer:
    name: "Comparison Agent"
    role: "Product Comparer"
    goal: "Generate objective product comparisons"
    backstory: "Expert at creating fair technical comparisons"
    tools: ["feature_matching", "markdown_generation"]
```

### Task Configuration (`config/tasks.yaml`)

This file defines the tasks assigned to each agent:

```yaml
tasks:
  research:
    description: "Research product specifications"
    agent: "researcher"
    expected_output: "Raw product data in JSON format"

  analysis:
    description: "Validate and normalise specifications"
    agent: "analyst"
    expected_output: "Validated product data in JSON format"

  comparison:
    description: "Generate product comparison"
    agent: "comparer"
    expected_output: "Markdown comparison report"
```

## Usage

### Basic Usage

Run the example script to see the system in action:

```bash
python src/example.py
```

This will compare sample products and generate a report in the `output/` directory.

### Custom Comparisons

To create custom product comparisons, use the main script:

```bash
python src/main.py --products "Product A, Product B, Product C" --category "Laptops"
```

Options:
- `--products`: Comma-separated list of products to compare (2-5 products)
- `--category`: Product category (e.g., Laptops, Smartphones, Cameras)
- `--output`: Custom output filename (default: category_comparison.md)
- `--detailed`: Generate a more detailed comparison (default: False)

### Programmatic Usage

You can also use the system programmatically in your Python code:

```python
from src.crew import ProductResearchCrew

# Initialize the crew
crew = ProductResearchCrew()

# Run a comparison
products = ["MacBook Pro 16", "Dell XPS 15", "ThinkPad X1 Carbon"]
category = "Laptops"
result = crew.run_comparison(products, category)

# Access the results
print(result.markdown_report)  # The full markdown report
print(result.feature_matrix)   # Just the feature comparison matrix
print(result.recommendations)  # Product recommendations
```

## Output Format

The system generates standardised markdown reports with the following sections:

1. **Introduction**: Overview of the compared products
2. **Methodology**: How the data was collected and analysed
3. **Feature Matrix**: Side-by-side comparison of technical specifications
4. **Detailed Analysis**: In-depth analysis of key features
5. **Recommendations**: Objective recommendations based on technical merit
6. **References**: Sources of the technical data

Example feature matrix:

```markdown
| Feature          | Product A       | Product B       | Product C       |
|------------------|-----------------|-----------------|-----------------|
| Processor        | Intel i7-1185G7 | AMD Ryzen 7 5800X | Intel i9-11900H |
| RAM              | 16GB LPDDR4X    | 32GB DDR4       | 64GB DDR4       |
| Storage          | 512GB NVMe SSD  | 1TB NVMe SSD    | 2TB NVMe SSD    |
| Display          | 13.4" 3840x2400 | 15.6" 2560x1440 | 17" 3840x2160   |
| Battery Life     | 10 hours        | 8 hours         | 6 hours         |
| Weight           | 1.2 kg          | 2.0 kg          | 2.5 kg          |
```

## Error Handling System

The AI Product Research System includes a comprehensive error handling system that provides:

1. **Structured Error Types**
   - `SystemError`: Base exception class for all system errors
   - `ConfigurationError`: For errors in configuration files or environment variables
   - `APIError`: For errors in API calls (OpenRouter, Serper)
   - `DataProcessingError`: For errors in data processing and transformation
   - `AgentError`: For errors in agent operations
   - `ValidationError`: For validation errors

2. **Error Severity Levels**
   - `INFO`: Informational messages that don't affect functionality
   - `WARNING`: Issues that don't stop execution but may affect results
   - `ERROR`: Serious issues that affect functionality but allow continued operation
   - `CRITICAL`: Fatal errors that prevent the system from functioning

3. **Error Handling Utilities**
   - `log_error()`: Logs errors with context information
   - `handle_error()`: Handles errors and returns structured responses
   - `safe_execute()`: Executes functions safely with error handling
   - `ErrorHandler`: Context manager for handling errors in a block of code
   - `retry()`: Decorator for automatic retries on failure

### Logging

The system creates detailed logs in the `logs/` directory with:
- Timestamp and severity level
- Error message and type
- Stack trace for debugging
- Context information about the operation that failed

Example log entry:
```
2025-06-04 09:15:23 - ai_product_research - ERROR - ERROR: Failed to extract specifications from https://example.com/product: Connection timeout
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify your API keys in the `.env` file
   - Check your internet connection
   - Run `python src/validate_dependencies.py` to verify API connectivity

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt` to ensure all dependencies are installed
   - Check for any error messages during installation

3. **Performance Issues**
   - Reduce the number of products being compared
   - Check system resources (CPU, memory)
   - Run `python src/test_performance.py` to identify bottlenecks

4. **Common Error Messages and Solutions**
   - `ConfigurationError: API key not found`: Add the required API key to your `.env` file
   - `APIError: Rate limit exceeded`: Wait before making more requests or upgrade your API plan
   - `DataProcessingError: Failed to extract specifications`: Check the URL and try a different product page
   - `ValidationError: Invalid product category`: Use one of the supported product categories
   - `AgentError: Agent communication failed`: Check your internet connection and API keys

### Error Recovery

The system includes automatic recovery mechanisms:
- Automatic retries for transient errors (network issues, rate limits)
- Graceful degradation when non-critical components fail
- Detailed error messages with suggested solutions

### Logging

The system creates logs in the `logs/` directory. Check these logs for detailed information about any issues. The log files follow this naming pattern:
- `ai_product_research.log`: Main application log
- `ai_product_research.error.log`: Error-only log for quick troubleshooting
- `ai_product_research.YYYY-MM-DD.log`: Daily rotated logs

## Advanced Features

### Custom Templates

You can create custom markdown templates in the `templates/` directory to modify the output format.

### Extending the System

The modular architecture allows for easy extension:

1. **Adding New Agents**: Modify `config/agents.yaml` to add new agent types
2. **Adding New Tasks**: Modify `config/tasks.yaml` to define new tasks
3. **Custom Data Sources**: Extend the `WebScraperAdapter` class to add new data sources

## Security Considerations

- API keys are stored in the `.env` file and should never be committed to version control
- All web data is sanitised before processing to prevent injection attacks
- The system does not store or transmit personal data

## Performance Expectations

- Average response time: < 120 seconds for a 3-product comparison
- Scaling: Performance may degrade with more than 5 products
- Resource usage: Minimal CPU and memory requirements

## Support and Feedback

For support or to provide feedback, please open an issue on the GitHub repository or contact the development team.
