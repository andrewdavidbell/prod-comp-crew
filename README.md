# AI Product Research System

An automated product research system using collaborative AI agents to generate objective technical comparisons from diverse sources.

## Features

- Configuration-driven architecture using YAML files
- OpenRouter integration with DeepSeek-chat model
- Serper API for web search capabilities
- Three-agent workflow (Researcher/Analyst/Comparer)
- Standardised markdown reports with feature matrices

## Requirements

- Python 3.9+
- OpenRouter API key
- Serper API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-product-research.git
cd ai-product-research
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:

```
OPENROUTER_API_KEY=your_openrouter_api_key
SERPER_API_KEY=your_serper_api_key
```

## System Validation

Before using the system, you can validate that everything is set up correctly:

```bash
python src/validate_system.py
```

This will:
- Validate all dependencies are installed
- Test API connectivity to OpenRouter and Serper
- Test basic agent communication

## Usage

To compare products, use the `main.py` script:

```bash
python src/main.py "Product A" "Product B" "Product C"
```

You can specify between 2 and 5 products to compare.

### Options

- `--validate`: Run system validation before starting the comparison
- `--output`: Specify a custom output file path (default: `output/comparison.md`)

Example:

```bash
python src/main.py "iPhone 15" "Samsung Galaxy S24" "Google Pixel 8" --validate --output custom_output.md
```

## Configuration

The system is configured using YAML files in the `config` directory:

- `agents.yaml`: Defines the agents, their roles, and LLM configurations
- `tasks.yaml`: Defines the tasks assigned to each agent and their dependencies

## Output

The system generates a standardised markdown report with:
- Product specifications
- Feature comparison matrix
- Objective analysis of strengths and weaknesses
- Technical recommendations

Output files are saved to the `output` directory by default.

## Development

The development plan is available in `cline-docs/development-plan.md`.

### Project Structure

```
.
├── config/                 # Configuration files
│   ├── agents.yaml         # Agent configurations
│   └── tasks.yaml          # Task configurations
├── src/                    # Source code
│   ├── crew.py             # Main crew implementation
│   ├── main.py             # Entry point script
│   ├── validate_dependencies.py  # Dependency validation
│   ├── test_api_connectivity.py  # API connectivity tests
│   ├── test_agent_communication.py  # Agent communication tests
│   └── validate_system.py  # System validation script
├── output/                 # Output directory for reports
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

## License

MIT
