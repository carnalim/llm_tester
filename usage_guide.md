# LLM Performance Tester - Usage Guide

This guide provides step-by-step instructions for common tasks in the modernized LLM Performance Tester application.

## Getting Started

After installing the dependencies with `pip install -r requirements.txt`, run the application:

```
python llm_tester.py
```

## Managing Profiles

### Creating a New Profile

1. Go to the "Profiles" tab
2. Click the "New" button in the bottom right
3. Fill in the profile details:
   - Profile Name: Enter a descriptive name
   - Provider: Select from OpenAI, Anthropic, OpenRouter, or Custom
   - API URL: Automatically populated based on provider selection
   - API Key: Enter your API key for the selected provider
   - Model: Either select from the dropdown or click "Fetch Models" to load available models
   - Content Type: Usually "application/json" (automatically set)
4. Click "Test Connection" to verify your credentials
5. Click "Save Profile" when complete

### OpenAI Profile Setup

1. Provider: Select "OpenAI"
2. API Key: Enter your OpenAI API key (from [OpenAI Dashboard](https://platform.openai.com/api-keys))
3. Click "Fetch Models" to load available models
4. Select your desired model (e.g., "gpt-3.5-turbo", "gpt-4")
5. Click "Save Profile"

### Anthropic Profile Setup

1. Provider: Select "Anthropic"
2. API Key: Enter your Anthropic API key (from [Anthropic Console](https://console.anthropic.com/))
3. Predefined Claude models will be loaded automatically
4. Select your desired model (e.g., "claude-3-opus-20240229")
5. Click "Save Profile"

### OpenRouter Profile Setup

1. Provider: Select "OpenRouter"
2. API Key: Enter your OpenRouter API key (from [OpenRouter Dashboard](https://openrouter.ai/keys))
3. Click "Fetch Models" to load available models from all providers
4. Select your desired model (e.g., "openai/gpt-4", "anthropic/claude-3-opus")
5. Click "Save Profile"

### Custom Provider Profile

1. Provider: Select "Custom"
2. Enter the API URL for your LLM provider
3. Enter your API key if required
4. Enter the model name or ID
5. Set the appropriate Content Type (usually "application/json")
6. Click "Save Profile"

## Running Performance Tests

1. Go to the "Run Test" tab
2. Select a profile from the dropdown at the top
3. Configure your test parameters:
   - Prompt: Enter the text prompt to send to the model
   - Max Tokens: Set the maximum number of tokens to generate
   - Temperature: Set the randomness factor (0.0-1.0)
   - Number of Runs: Set how many iterations to perform (3+ recommended)
4. Click "Run Test"
5. Watch real-time results appear in the results panel
6. When complete, review the results and click "Save Results" to store them
7. Optionally use "Copy to Clipboard" to copy the results text

## Comparing Test Results

1. Go to the "Compare Results" tab
2. Select two or more saved test results from the list
   - Hold Ctrl/Cmd while clicking to select multiple items
3. Click "Compare Selected"
4. Review the color-coded bar chart showing TPS (Tokens Per Second) for each model
5. Analyze the performance differences
6. Use "Export Selected" to save the comparison data for further analysis

## Using the Settings Tab

### Changing UI Theme

1. Go to the "Settings" tab
2. Under "Application Settings", find the "UI Theme" dropdown
3. Select either "light" or "dark" theme
4. The theme will apply immediately

### Setting Default Parameters

1. Go to the "Settings" tab
2. Under "Default Test Parameters", you can configure:
   - Default Max Tokens
   - Default Temperature
   - Default Number of Runs
3. These defaults will be applied to new tests

### Managing Data

1. Go to the "Settings" tab
2. Under "Data Management", you can:
   - Export All Results: Save all test data to JSON or CSV
   - Import Results: Load previously exported results
   - Clear All Results: Delete all stored test data (with confirmation)

## Using the Token Counter Utility

The token counter utility helps estimate token usage for different prompts:

1. Run the token counter:
   ```
   python token_counter.py
   ```
2. Enter your prompt text in the input area
3. Click "Count Tokens" to see estimates using different counting methods
4. Use the "Sample Prompts" dropdown to try predefined examples

## Data Export and Import

### Exporting Results

1. Go to the "Compare Results" tab
2. Select the results you want to export
3. Click "Export Selected"
4. Choose a file format:
   - JSON: Preserves all data details
   - CSV: Better for spreadsheet analysis
5. Select a location to save the file

### Importing Results

1. Go to the "Settings" tab
2. Click "Import Results"
3. Select a previously exported JSON file
4. The imported results will be added to your existing results

## Tips for Accurate Testing

### Eliminating Variables

For the most accurate comparisons:
- Use identical prompts for all tests
- Run tests at similar times of day
- Use the same max_tokens and temperature settings
- Run multiple iterations for each test (3-5 is recommended)
- Test from the same network environment

### Sample Prompts for Testing

Here are some effective prompts for performance testing:

**Short Creative Task**
```
Write a short poem about artificial intelligence.
```

**Medium Analytical Task**
```
Explain the difference between supervised and unsupervised learning in machine learning. Provide examples of each.
```

**Long Generation Task**
```
Write a creative story about a robot who wants to become human. Include character development, dialogue, and a conclusion.
```

### Interpreting Results

- **TPS (Tokens Per Second)**: Higher is better
- Consider both speed and quality for overall evaluation
- Network latency may affect results
- Some models may start slowly but generate subsequent tokens faster
- Compare models from the same provider for most accurate relative performance

### Limitations

- The application estimates tokens when the API doesn't provide token counts
- Results may vary based on API load and network conditions
- Some providers may have rate limits that affect performance during testing
- Performance can vary based on prompt complexity and length

## Troubleshooting

### Connection Issues

If you encounter connection problems:
- Verify your internet connection
- Check if the provider's API is operational
- Try using the "Test Connection" feature in the Profiles tab
- Ensure your API key has not expired

### API Errors

If you receive API errors:
- Verify your API key is correct and has sufficient permissions
- Check that your account has access to the requested model
- Ensure you're using the correct API URL for the provider
- Verify that your Content Type setting is appropriate

### Model Fetching Issues

If "Fetch Models" doesn't work:
- Check your API key permissions
- Verify the provider supports model listing
- Try entering the model name manually
- For newer models, you may need to enter the name manually

### Empty or Incomplete Results

If you get empty results:
- Check if your prompt is too short or unclear
- Verify the max_tokens setting is reasonable
- Ensure the temperature setting is in the valid range (0.0-1.0)
- Try running fewer iterations to avoid rate limits