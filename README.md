# Gcode Academy Agent

This is the backend AI assistant for the Gcode Academy app. It provides a FastAPI-based API server that integrates with OpenAI's API to power the in-app tutoring assistant.

## How to Run

```bash
# Install dependencies
make install

# Run the backend server (http://localhost:8000)
make run
```

## Features

- OpenAI API integration for natural language tutoring
- FastAPI-powered REST API
- Support for conversation context and history
- Optimized for programming education assistance

## Structure

- `src/agent/` - Core AI functionality and OpenAI integration
- `src/api/` - FastAPI application and endpoints
- `tests/` - Test suite using pytest

## Testing

```bash
# Run all tests
make test

# Run linting with Ruff
make lint
```

## Setup

To use this backend, you'll need:

1. An OpenAI API key
2. Python 3.13+
3. Poetry for dependency management

Create a `.env` file in the project root with:

- OPENAI_API_KEY=your_api_key_here
