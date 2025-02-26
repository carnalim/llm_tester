# LLM Performance Tester

A modern Python application for measuring and comparing the performance of various Large Language Models (LLMs) in terms of Tokens Per Second (TPS).

![LLM Performance Tester](screenshot.png)

## Features

### Improved User Interface
- Modern, responsive UI with light and dark themes
- Intuitive navigation with tabbed interface
- Real-time test results and visual charts
- Streamlined workflow for testing and comparison

### Provider Management
- Create and manage profiles for different LLM providers:
  - OpenAI (GPT-3.5, GPT-4, etc.)
  - Anthropic (Claude models)
  - OpenRouter (access to multiple providers)
  - Custom APIs (self-hosted models, other providers)
- Automatic model selection from provider APIs
- Test connection functionality
- Secure API key storage

### Performance Testing
- Configure comprehensive test parameters
- Run performance tests with multiple iterations
- Real-time results display with TPS metrics
- Save and organize test results

### Results Management
- Visual comparison of performance across models
- Export results to JSON or CSV formats
- Filter and sort test results
- Delete or archive old results

### Utilities
- Token counter utility to estimate token usage
- Default parameter templates
- Configuration settings

## Requirements

- Python 3.6+
- Tkinter (usually included with Python)
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - matplotlib
  - pillow

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python llm_tester.py
   ```

2. Create Provider Profiles:
   - Go to the "Profiles" tab
   - Click "New" to create a profile
   - Enter a name for your profile
   - Select a provider type (OpenAI, Anthropic, OpenRouter, or Custom)
   - Enter your API key and other required information
   - Click "Fetch Models" to retrieve available models (or enter manually)
   - Test your connection to verify credentials
   - Click "Save Profile"

3. Run Performance Tests:
   - Go to the "Run Test" tab
   - Select a profile from the dropdown
   - Configure your test parameters (prompt, max tokens, etc.)
   - Click "Run Test"
   - View real-time results
   - Click "Save Results" to store the results for future comparison

4. Compare Test Results:
   - Go to the "Compare Results" tab
   - Select multiple test results from the list
   - Click "Compare Selected" to generate a comparison chart
   - Export results for further analysis

5. Use the Settings Tab:
   - Configure UI theme
   - Set default test parameters
   - Manage data with import/export options

## Supported Providers

The application supports the following LLM providers:

### OpenAI
- API URL: https://api.openai.com/v1/chat/completions
- Models: gpt-3.5-turbo, gpt-4, etc.
- Automatically fetches available models

### Anthropic
- API URL: https://api.anthropic.com/v1/messages
- Models: claude-3-opus-20240229, claude-3-sonnet, etc.
- Includes predefined list of Claude models

### OpenRouter
- API URL: https://openrouter.ai/api/v1/chat/completions
- Models: Various models from different providers
- Supports model discovery via API

### Custom
- Configure your own API URL, headers, and model name
- Useful for connecting to local or custom LLM endpoints
- Supports standard API formats

## Data Storage

The application stores profiles and test results in the following files:
- llm_profiles.json: Contains saved provider profiles
- llm_test_results.json: Contains saved test results

## Token Counter Utility

The included `token_counter.py` helps estimate token usage for prompts:
```
python token_counter.py
```

## Best Practices

For accurate performance testing:
- Run multiple iterations (3+ recommended)
- Use consistent prompts for comparing different models
- Test during similar times of day to account for API load variations
- Consider network latency when interpreting results
- Export and analyze results for detailed comparison