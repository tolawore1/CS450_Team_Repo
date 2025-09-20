# AI Model Catalog CLI

A command-line interface for evaluating the trustworthiness and quality of AI/ML models from GitHub repositories and Hugging Face Hub. This tool helps engineering teams make informed decisions about model reuse by providing comprehensive scoring across multiple quality dimensions.

## Team

- **Ethan** - Backend Development & API Integration
- **Ali** - Metrics Implementation & Scoring Algorithms  
- **Fahd** - CLI Interface & User Experience
- **Taiwo** - Testing & Quality Assurance

## Overview

The AI Model Catalog CLI evaluates AI/ML models across eight key dimensions to provide a comprehensive NetScore that helps teams assess model trustworthiness and reusability:

- **Size Score** - Model size compatibility across different hardware platforms
- **License** - License clarity and compatibility with LGPLv2.1
- **Ramp-up Time** - Documentation quality and ease of adoption
- **Bus Factor** - Maintainer availability and project sustainability
- **Availability** - Presence of code and dataset
- **Dataset Quality** - Dataset documentation and quality indicators
- **Code Quality** - Code style, testing, and maintainability
- **Performance Claims** - Evidence of performance benchmarks

## Features

- 🔍 **Dual Source Support** - Analyze models from both GitHub repositories and Hugging Face Hub
- ⚡ **Parallel Processing** - Metrics calculated concurrently for optimal performance
- 📊 **Comprehensive Scoring** - 8-dimensional evaluation with weighted NetScore
- 🖥️ **Interactive Mode** - User-friendly interface for model exploration
- 📈 **Performance Metrics** - Latency measurements for each scoring component
- 🔧 **Extensible Design** - Modular architecture for easy metric addition

## Installation

### Prerequisites

- Python 3.10 or higher
- Git (for repository analysis)
- Internet connection (for API calls)

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd CS450_Team_Repo

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Enable pre-commit hooks
pre-commit install

# 4. Set up environment variables (optional)
export GITHUB_TOKEN="your_github_token_here"  # For higher rate limits
export LOG_FILE="catalog.log"                 # For logging
export LOG_LEVEL="1"                          # 0=silent, 1=info, 2=debug
```

## Usage

### Command Line Interface

#### Analyze GitHub Repository
```bash
# Basic usage
catalog models --owner huggingface --repo transformers

# With custom parameters
catalog models --owner microsoft --repo DeepSpeed
```

#### Analyze Hugging Face Model
```bash
# Basic usage
catalog hf-model --model-id bert-base-uncased

# With custom model
catalog hf-model --model-id microsoft/DialoGPT-medium
```

#### Interactive Mode
```bash
# Launch interactive browser
catalog interactive
```

### Auto-Grader Interface

The tool supports the required auto-grader interface for automated evaluation:

```bash
# Install dependencies
./run install

# Process URL file
./run /path/to/url_file.txt

# Run test suite
./run test
```

## Output Format

The CLI provides detailed scoring information in both human-readable and machine-readable formats:

### Human-Readable Output
```
Repo: huggingface/transformers ⭐ 45,231
Description: State-of-the-art Natural Language Processing for PyTorch and TensorFlow
Language: Python
Updated: 2024-01-15T10:30:00Z
Stars: 45,231
Forks: 10,847
Open issues: 234
Size: 12,456 KB
License: Apache-2.0

NetScore Breakdown:
size: 0.988
license: 1.000
ramp_up_time: 1.000
bus_factor: 1.000
availability: 1.000
dataset_quality: 0.750
code_quality: 0.875
performance_claims: 0.500
NetScore: 0.889
```

### NDJSON Output (Auto-Grader)
```json
{
  "name": "huggingface/transformers",
  "category": "MODEL",
  "net_score": 0.889,
  "net_score_latency": 150,
  "ramp_up_time": 1.000,
  "ramp_up_time_latency": 25,
  "bus_factor": 1.000,
  "bus_factor_latency": 15,
  "performance_claims": 0.500,
  "performance_claims_latency": 30,
  "license": 1.000,
  "license_latency": 10,
  "size_score": {
    "raspberry_pi": 0.200,
    "jetson_nano": 0.400,
    "desktop_pc": 0.800,
    "aws_server": 0.950
  },
  "size_score_latency": 45,
  "dataset_and_code_score": 1.000,
  "dataset_and_code_score_latency": 20,
  "dataset_quality": 0.750,
  "dataset_quality_latency": 35,
  "code_quality": 0.875,
  "code_quality_latency": 40
}
```

## Scoring Methodology

### Size Score
Evaluates model size compatibility across different hardware platforms:
- **Raspberry Pi** - Ultra-low power devices (< 1GB RAM)
- **Jetson Nano** - Edge AI devices (2-4GB RAM)
- **Desktop PC** - Standard development machines (8-16GB RAM)
- **AWS Server** - Cloud instances (16GB+ RAM)

### License Score
Assesses license compatibility with LGPLv2.1:
- **1.0** - Compatible licenses (MIT, Apache-2.0, BSD, etc.)
- **0.0** - Incompatible or proprietary licenses

### Ramp-up Time Score
Measures documentation quality and ease of adoption:
- **1.0** - Comprehensive README (250+ characters)
- **0.0** - Minimal or missing documentation

### Bus Factor Score
Evaluates project sustainability:
- **1.0** - Multiple maintainers available
- **0.0** - Single point of failure

### Availability Score
Checks for code and dataset presence:
- **1.0** - Both code and dataset available
- **0.0** - Missing code or dataset

### Dataset Quality Score
Assesses dataset documentation and quality:
- **1.0** - Well-documented with known datasets
- **0.0** - Poor or missing dataset information

### Code Quality Score
Evaluates code maintainability:
- **1.0** - Tests, CI, linting, and documentation
- **0.0** - No quality indicators

### Performance Claims Score
Measures evidence of performance benchmarks:
- **1.0** - State-of-the-art claims with evidence
- **0.0** - No performance claims

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token for higher rate limits | None |
| `LOG_FILE` | Path to log file | `catalog.log` |
| `LOG_LEVEL` | Log verbosity (0=silent, 1=info, 2=debug) | `0` |

### Metric Weights

The NetScore calculation uses the following weights (configurable):

```python
weights = {
    "size": 0.1,
    "license": 0.15,
    "ramp_up_time": 0.15,
    "bus_factor": 0.1,
    "availability": 0.1,
    "dataset_quality": 0.1,
    "code_quality": 0.15,
    "performance_claims": 0.15,
}
```

## Logging

This app writes logs to a file based on two environment variables:

- `LOG_FILE` — the path to the log file
- `LOG_LEVEL` — verbosity: `"0"` (silent, default), `"1"` (info), `"2"` (debug)

If `LOG_LEVEL=0` or `LOG_FILE` is unset, no log output is written.

### Quick start (PowerShell/bash)

```powershell
$env:LOG_LEVEL="2"               # 0=silent, 1=info, 2=debug
$env:LOG_FILE="$PWD\logs\catalog.log"
python -m ai_model_catalog.cli models --owner huggingface --repo transformers
Get-Content .\logs\catalog.log

bash
export LOG_LEVEL=2               # 0=silent, 1=info, 2=debug
export LOG_FILE="$PWD/logs/catalog.log"
python -m ai_model_catalog.cli models --owner huggingface --repo transformers
cat ./logs/catalog.log

Format
YYYY-MM-DD HH:MM:SS LEVEL logger: message
examples:
2025-09-19 19:30:18 INFO catalog: models command: owner=huggingface repo=transformers
2025-09-19 19:30:18 DEBUG ai_model_catalog.fetch_repo: OK https://api.github.com/repos/huggingface/transformers status=200 len=12345
2025-09-19 19:30:19 INFO ai_model_catalog.score_model: NetScore=0.842

```

## Development

### Project Structure

```
.
├── src/ai_model_catalog/          # Main package
│   ├── __init__.py
│   ├── __main__.py               # Entry point
│   ├── cli.py                    # CLI interface
│   ├── fetch_repo.py             # API integration
│   ├── score_model.py            # NetScore calculation
│   └── metrics/                  # Individual metrics
│       ├── __init__.py
│       ├── base.py               # Metric base class
│       ├── runner.py             # Parallel execution
│       ├── types.py              # Data types
│       └── score_*.py            # Individual metrics
├── tests/                        # Test suite
├── pyproject.toml                # Dependencies & config
├── .pre-commit-config.yaml       # Git hooks
├── .pylintrc                     # Linting rules
├── pytest.ini                    # Test configuration
└── run                           # Auto-grader interface
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run auto-grader test command
./run test
```

### Code Quality

```bash
# Run linting
pylint src tests

# Format code
black src tests

# Sort imports
isort src tests

# Run all quality checks
pre-commit run --all-files
```

## API Integration

### GitHub API
- Repository metadata (stars, forks, issues, etc.)
- README content and documentation
- Commit history and contributors
- GitHub Actions workflow runs

### Hugging Face Hub API
- Model metadata and downloads
- Model files and artifacts
- Dataset information
- Performance metrics

## Performance

The tool is optimized for performance with:
- **Parallel metric calculation** using ThreadPoolExecutor
- **Efficient API usage** with proper rate limiting
- **Caching mechanisms** for repeated requests
- **Minimal memory footprint** for large models

Typical performance on a modern machine:
- **GitHub repositories**: 2-5 seconds
- **Hugging Face models**: 1-3 seconds
- **Parallel processing**: 3-4x speedup

## Troubleshooting

### Common Issues

**Rate Limit Exceeded**
```bash
# Set GitHub token for higher limits
export GITHUB_TOKEN="your_token_here"
```

**Permission Denied on `./run`**
```bash
# Make executable
chmod +x run
```

**Import Errors**
```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL="2"
catalog models --owner huggingface --repo transformers
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hugging Face for the model ecosystem
- GitHub for repository hosting and API
- The open-source community for inspiration and tools

---

**Note**: This tool is designed for educational purposes as part of CS450 Software Engineering coursework. Use in production environments at your own risk.
