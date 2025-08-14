# SweCli - Software Engineering CLI Tool

SWE CLI is an intelligent software engineering automation tool that bridges Jira issue tracking with Azure DevOps repositories using AI-powered code generation. It fetches development tasks from Jira and automatically implements them by leveraging the Codex CLI with Model Context Protocol (MCP) for comprehensive codebase understanding.

## Project Architecture & Design

### Core Workflow
1. **Issue Fetching**: Retrieves detailed information from Jira tickets including descriptions, labels, and metadata
2. **Context Building**: Generates comprehensive development context using Azure DevOps MCP tools
3. **AI Code Generation**: Uses Codex CLI with full repository context to implement the requested changes
4. **Automated Execution**: Runs in sandbox mode with full access to make actual code changes

### Key Components

#### 1. Jira Integration (`src/jira_fetch.py`)
- Connects to Jira using API tokens for secure authentication
- Fetches complete issue details including:
  - Issue key, summary, and description
  - Labels and issue type
  - Project information
  - Raw issue data for additional context

#### 2. Azure DevOps Context Generation (`src/mcp_context.py`)
- Builds intelligent context instructions for MCP servers
- Generates targeted repository exploration commands:
  - Repository information retrieval
  - Branch and pull request analysis
  - Code search within specific modules
  - Work item linking analysis
- Provides risk assessment and testing guidance

#### 3. Configuration Management (`src/config.py`)
- Environment-based configuration using `.env` files
- Supports multiple service integrations:
  - **Jira**: Server URL, username, API token
  - **Azure DevOps**: Organization, project, repository, PAT
  - **OpenAI**: API key for Codex integration

#### 4. Advanced Logging (`src/logging_setup.py`)
- Configurable logging with multiple output formats
- Environment-controlled log levels and destinations
- JSON structured logging for production environments
- File and console output options

#### 5. Codex Integration (`src/codex_codegen.py`)
- Executes Codex CLI with full automation enabled
- Runs in "danger-full-access" sandbox mode for complete repository access
- Passes structured prompts with Jira context and MCP instructions

#### 6. Main Orchestrator (`src/main.py`)
- Command-line interface for the entire workflow
- Argument parsing and validation
- Coordinates all components in the proper sequence

### MCP (Model Context Protocol) Integration

The tool is designed to work with MCP servers, specifically:
- **Azure DevOps MCP Server**: Provides repository context, PR analysis, and work item integration
- **Configuration**: Uses `codex.config.toml` for MCP server setup
- **Dynamic Context**: Builds repository-specific exploration instructions
- **Context Window Management**: Intelligent prompt size management to prevent token limit errors

### Context Window Management

SweCli includes sophisticated context window management to prevent "input exceeds context window" errors:

- **Automatic Token Counting**: Uses tiktoken for accurate token estimation across different models
- **Model-Aware Limits**: Built-in knowledge of context windows for GPT-4, GPT-3.5, Claude 3, and other models
- **Intelligent Truncation**: Smart content summarization that preserves important information
- **Configurable Safety Margins**: Adjustable limits to ensure prompts fit comfortably
- **MCP Output Management**: Handles large MCP tool outputs gracefully

**Configuration Options:**
```bash
export MODEL_NAME=gpt-4                    # Target model for token counting
export MAX_CONTEXT_TOKENS=8192            # Override model default limit  
export CONTEXT_SAFETY_MARGIN=0.8          # Use 80% of available context
```

### Prompt Engineering (`prompts/`)

The system uses structured prompt templates that:
- **Basic Template (`codegen.md`)**: Embeds complete Jira issue information as JSON, includes dynamically generated context instructions, and provides clear requirements for code implementation
- **Test Generation Template (`codegen_with_tests.md`)**: Enhanced version that additionally focuses on comprehensive test generation including:
  - Unit tests for individual functions/methods
  - Integration tests where appropriate
  - Edge case and error handling tests
  - Mock tests for external dependencies
  - Following existing test patterns and pytest conventions
- Ensures proper testing and repository convention adherence

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for MCP Azure DevOps server)
- Access to Jira and Azure DevOps instances
- Codex CLI installed and configured

### Environment Configuration

Create a `.env` file with the following variables:

```env
# Jira Configuration
JIRA_SERVER=https://your-instance.atlassian.net
JIRA_USER=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Azure DevOps Configuration
ADO_ORG=your-organization
ADO_PROJECT=your-project
ADO_REPO=repo1,repo2,repo3
ADO_PAT=your-personal-access-token

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Optional Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=plain
LOG_FILE=/path/to/logfile.log
```

### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command
```bash
python -m src.main --jira EP-1234 --ado-repo "frontend-app,backend-api"
```

### Command Line Options
- `--jira`: Jira issue key (required)
- `--ado-org`: Azure DevOps organization (defaults to env var)
- `--ado-project`: Azure DevOps project (defaults to env var)
- `--ado-repo`: Comma or space-separated list of repositories to analyze
- `--workspace`: Directory where code changes should be applied (defaults to current directory)
- `--generate-tests`: Generate comprehensive tests for the requirements in addition to the main implementation

### Example Workflow

1. **Basic Implementation**: 
   ```bash
   python -m src.main --jira PROJ-123 --ado-repo "web-app,api-service"
   ```

2. **Implementation with Test Generation**: 
   ```bash
   python -m src.main --jira PROJ-123 --ado-repo "web-app,api-service" --generate-tests
   ```

3. **The tool will**:
   - Connect to Jira and fetch issue PROJ-123
   - Generate Azure DevOps context for web-app and api-service repositories
   - Create a comprehensive prompt with issue details and repository context
   - If `--generate-tests` is specified, use the enhanced prompt template for test generation
   - Execute Codex CLI to implement the changes (and tests if requested)
   - Apply changes directly to the specified workspace

## Architecture Benefits

### 1. **Separation of Concerns**
- Each module handles a specific aspect of the workflow
- Clean interfaces between Jira, Azure DevOps, and AI components
- Configurable and testable components

### 2. **Extensibility**
- Easy to add new issue tracking systems
- Pluggable MCP server support
- Configurable prompt templates

### 3. **Production Ready**
- Comprehensive logging and error handling
- Environment-based configuration
- Secure credential management

### 4. **AI-Enhanced Development**
- Leverages repository context for better code generation
- Understands project structure and conventions
- Provides risk assessment and testing guidance

## Development & Contributing

### Project Structure
```
SweCli/
├── src/                    # Main application code
│   ├── __init__.py        # Package initialization
│   ├── main.py            # CLI entry point and orchestration
│   ├── config.py          # Environment configuration management
│   ├── jira_fetch.py      # Jira API integration
│   ├── mcp_context.py     # Azure DevOps context generation
│   ├── codex_codegen.py   # Codex CLI integration
│   └── logging_setup.py   # Advanced logging configuration
├── prompts/               # AI prompt templates
│   ├── codegen.md         # Main code generation prompt
│   └── codegen_with_tests.md  # Enhanced prompt for test generation
├── requirements.txt       # Python dependencies
├── codex.config.toml     # MCP server configuration
└── README.md             # This file
```

### Running Tests

#### Local Development
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run linting and formatting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
pylint src/
```

#### CI/CD Pipeline
The project uses GitHub Actions for continuous integration with the following jobs:

- **Code Quality & Linting**: Black, isort, flake8, mypy, pylint, bandit, safety
- **Test Suite**: Multi-platform testing (Ubuntu, Windows, macOS) across Python 3.8-3.12
- **Integration Tests**: Real MCP server testing on main branch
- **Build**: Package building and validation
- **Docker**: Multi-architecture container builds
- **Security Scanning**: Trivy vulnerability scanning
- **Release**: Automated PyPI publishing on releases

## Security Considerations

- API tokens and credentials are loaded from environment variables
- No sensitive information is logged by default
- Codex runs in controlled sandbox environment
- Repository access is explicitly controlled through configuration

## Future Enhancements

- Support for additional issue tracking systems (GitHub Issues, Linear, etc.)
- Enhanced repository analysis and context generation
- Integration with additional MCP servers
- Automated testing and validation workflows
- CI/CD pipeline integration for automated development workflows