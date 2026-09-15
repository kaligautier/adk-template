# Contributing to Google ADK Template

Thank you for your interest in contributing to the Google ADK Template! This document provides guidelines for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- [Just command runner](https://github.com/casey/just)
- Google Cloud Project with Vertex AI enabled

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/google-adk-template.git
cd google-adk-template

# Install dependencies
just install

# Configure environment
cp .env.example .env
# Edit .env with your GCP project details
```

## Development Workflow

### Code Quality Standards

This project maintains high code quality standards. All contributions must:

1. **Pass all quality checks**: Run `just pre-commit` before committing
2. **Maintain test coverage**: Keep coverage at or above 83%
3. **Follow code style**: Use `just format` to format code
4. **Pass linting**: Use `just lint` to check for issues

### Available Commands

```bash
just install      # Install dependencies
just api          # Run API server (development mode)
just format       # Format code with ruff
just lint         # Lint code with ruff
just test         # Run tests with coverage
just pre-commit   # Run all quality checks (format + lint + test)
just build        # Build Docker image
just run          # Run Docker container
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the existing code style and architecture patterns
   - Keep changes focused and atomic
   - Write clear, descriptive commit messages

3. **Test your changes**:
   ```bash
   just test
   ```

4. **Run quality checks**:
   ```bash
   just pre-commit
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add calculator tool with division operation
fix: handle division by zero in calculator service
docs: update architecture decision for services layer
test: add integration tests for time service
```

## Pull Request Process

1. **Update documentation**: If your changes affect functionality, update relevant docs

2. **Ensure CI passes**: All GitHub Actions workflows must pass:
   - Tests workflow
   - Linting workflow
   - Docker build workflow

3. **Write a clear PR description**:
   - What does this PR do?
   - Why is this change needed?
   - How has it been tested?
   - Any breaking changes?

4. **Link related issues**: Reference any related issues in the PR description

5. **Request review**: Wait for maintainer review and address feedback

## Architecture Guidelines

This template follows specific architectural patterns. Please maintain consistency:

### Hexagonal Architecture

- **Services Layer** (`services/`): Pure Python business logic, no ADK dependencies
- **Tools Layer** (`components/tools/custom/`): Thin ADK wrappers that call services
- **Agents Layer** (`components/agents/`): Agent definitions with tools and callbacks
- **Config Layer** (`config/`): Environment-driven configuration

### Adding New Components

#### Adding a New Tool

1. **Create service** (if logic is reusable):
   ```python
   # services/my_service.py
   def process_data(data: dict) -> dict:
       """Pure Python logic - no ADK dependencies."""
       return {"processed": data}
   ```

2. **Create tool**:
   ```python
   # components/tools/custom/my_tool.py
   from google.adk.tools import ToolContext
   from app.services.my_service import process_data

   async def my_tool(data: dict, tool_context: ToolContext) -> dict:
       """Thin ADK wrapper."""
       return process_data(data)
   ```

3. **Add tests**:
   ```python
   # test/unit/services/test_my_service.py
   def test_process_data():
       result = process_data({"input": "test"})
       assert result["processed"] == {"input": "test"}
   ```

4. **Update agent** to include the new tool

#### Adding a New Agent

1. Create folder: `components/agents/my_agent/`
2. Create `agent.py` with variable matching folder name
3. Export agent: `my_agent = LlmAgent(...)`
4. Add tests in `test/unit/components/agents/`

## Testing Guidelines

### Test Coverage Requirements

- Maintain overall coverage at or above 83%
- All new code should be tested
- Write both unit and integration tests

### Test Organization

```
test/
├── unit/
│   ├── services/           # Service layer tests (fast)
│   ├── components/         # Tool and agent tests
│   └── utils/              # Utility tests
└── conftest.py             # Test fixtures
```

### Running Tests

```bash
# Run all tests
just test

# Run specific test file
uv run pytest test/unit/services/test_calculator_service.py

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=app --cov-report=html
```

## Reporting Issues

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach (if applicable)
- Any breaking changes or dependencies

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility and apologize for mistakes
- Focus on what is best for the community

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Questions?

If you have questions about contributing:
- Open a GitHub Discussion
- Review existing issues and PRs
- Check the documentation in the `docs/` folder

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
