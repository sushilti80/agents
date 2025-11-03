# Contributing to Daedalus Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
5. **Start Qdrant:**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

## Making Changes

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new features
4. Update documentation as needed
5. Ensure all tests pass
6. Commit with descriptive messages

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Add docstrings for classes and functions
- Keep functions focused and small
- Use meaningful variable names

## Testing

Run tests before submitting:
```bash
pytest tests/ -v
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CHANGELOG.md

## Pull Request Process

1. Update documentation and tests
2. Ensure all tests pass
3. Update CHANGELOG.md
4. Create PR with clear description
5. Wait for review

## Questions?

Open an issue for discussion before starting major changes.

Thank you for contributing! 🎉
