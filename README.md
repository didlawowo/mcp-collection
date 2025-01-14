# Datadog Model Context Protocol (MCP) 🔍

A Python-based tool to interact with Datadog API and fetch monitoring data from your infrastructure. This MCP provides easy access to monitor states and Kubernetes logs through a simple interface.

## Features 🌟

- **Monitor State Tracking**: Fetch and analyze specific monitor states
- **Kubernetes Log Analysis**: Extract and format error logs from Kubernetes clusters
- **Structured Output**: JSON formatted responses for easy integration

## Prerequisites 📋

- Python 3.11+
- Datadog API and Application keys
- Access to Datadog  site

## Installation 🔧

```bash
pip install -r requirements.txt
```

Required packages:

```text
datadog-api-client
fastmcp
loguru
icecream
python-dotenv

```

## Environment Setup 🔑

Create a `.env` file with your Datadog credentials:

```env
DD_API_KEY=your_api_key
DD_APP_KEY=your_app_key
```

## Usage 💻

### Monitor State Check

```python
# Get state of a specific monitor
response = get_monitor_states(name="traefik")
```

### Kubernetes Log Analysis

```python
# Get error logs from a cluster
logs = get_k8s_logs(
    cluster="your-cluster-name",
    timeframe=3,  # Hours to look back
    namespace="optional-namespace"  # Optional namespace filter
)
```

## Error Handling 🚨

The tool includes:

- Detailed error messages
- Logging with loguru
- JSON serialization safety checks

## Architecture 🏗

- **FastMCP Base**: Utilizes FastMCP framework for tool management
- **Modular Design**: Separate functions for monitors and logs
- **Type Safety**: Full typing support with Python type hints
- **API Abstraction**: Wrapped Datadog API calls with error handling

## Contributing 🤝

Feel free to:

1. Open issues for bugs
2. Submit PRs for improvements
3. Add new features

## Notes 📝

- API calls are made to Datadog EU site
- Default timeframe is 1 hour for monitor states
- Page size limits are set to handle most use cases

Would you like me to add any specific section or elaborate on any part?