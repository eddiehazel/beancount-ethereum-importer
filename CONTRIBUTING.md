# Contributing to beancount-ethereum-importer

Thank you for your interest in contributing to beancount-ethereum-importer! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip
- git

### Setting Up Your Development Environment

1. Fork the repository on GitHub

2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/beancount-ethereum-importer.git
cd beancount-ethereum-importer
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. Install the package in development mode:
```bash
pip install -e .
```

## Running Tests

We use pytest for testing. Run the full test suite with:

```bash
PYTHONPATH=. pytest tests/ -v
```

Run tests with coverage:

```bash
PYTHONPATH=. pytest tests/ --cov=beancount_ethereum --cov-report=term-missing
```

Run a specific test file:

```bash
PYTHONPATH=. pytest tests/test_importer.py -v
```

Run a specific test:

```bash
PYTHONPATH=. pytest tests/test_importer.py::TestImporterExtract::test_extract_basic_transaction -v
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

## Making Changes

### Branching Strategy

1. Create a feature branch from `main`:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them with clear, descriptive messages:
```bash
git commit -m "Add support for ERC-721 token transfers"
```

3. Push to your fork:
```bash
git push origin feature/your-feature-name
```

4. Open a Pull Request on GitHub

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues and pull requests when relevant

### Pull Request Guidelines

- Provide a clear description of the changes
- Include any relevant issue numbers
- Ensure all tests pass
- Update documentation if necessary
- Add tests for new functionality

## Project Structure

```
beancount-ethereum-importer/
├── beancount_ethereum/
│   ├── __init__.py       # Package initialization and exports
│   ├── __main__.py       # CLI entry point for downloading
│   ├── downloader.py     # Block explorer API client
│   └── importer.py       # Beangulp importer implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Shared pytest fixtures
│   ├── test_downloader.py
│   └── test_importer.py
├── docs/                  # Additional documentation
├── config.json.example   # Example configuration
├── import_config.py.example
├── requirements.txt      # Runtime dependencies
├── requirements-dev.txt  # Development dependencies
├── setup.py              # Package configuration
├── pytest.ini            # Pytest configuration
└── README.md
```

## Adding New Features

### Adding a New Block Explorer

1. The `BlockExplorerApi` class in `downloader.py` is designed to work with Etherscan-compatible APIs
2. If the new explorer has a different API format, you may need to add adapter methods
3. Add tests for any new functionality

### Adding New Transaction Types

1. Add a new method to `BlockExplorerApi` (e.g., `get_erc721_transfers`)
2. Call it from the `download` function
3. Update the importer if necessary to handle the new data format
4. Add comprehensive tests

### Modifying the Importer

1. The `Importer` class inherits from `beangulp.Importer`
2. Required methods: `identify()`, `account()`, `extract()`
3. Keep backward compatibility with existing configurations

## Testing Guidelines

### Writing Tests

- Use descriptive test names that explain what's being tested
- Group related tests in classes
- Use fixtures for common setup
- Test both success and failure cases
- Mock external dependencies (API calls)

### Test Structure

```python
class TestFeatureName:
    """Tests for feature description."""

    def test_specific_behavior(self, fixture):
        """Test that specific behavior works correctly."""
        # Arrange
        input_data = ...

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected_value
```

## Reporting Issues

When reporting issues, please include:

1. Python version
2. Package version
3. Operating system
4. Complete error message and traceback
5. Minimal reproduction steps
6. Configuration (with sensitive data removed)

## Getting Help

- Open an issue on GitHub for bugs or feature requests
- Check existing issues before creating a new one
- Provide as much context as possible

## License

By contributing to this project, you agree that your contributions will be licensed under the GPL-3.0 license.
