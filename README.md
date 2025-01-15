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
uv
```

## Environment Setup 🔑

Create a `.env` file with your Datadog credentials:

```env
DD_API_KEY=your_api_key
DD_APP_KEY=your_app_key
```

## Usage 💻

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

I'll add a section about MCP and Claude Desktop setup:

# Model Context Protocol (MCP) Introduction 🤖

## What is MCP?

Model Context Protocol (MCP) is a framework allowing AI models to interact with external tools and APIs in a standardized way. It enables models like Claude to:

- Access external data
- Execute commands
- Interact with APIs
- Maintain context across conversations

## some examples of MCP servers

<https://github.com/punkpeye/awesome-mcp-servers?tab=readme-ov-file>

## Tutorial for setup MCP

<https://medium.com/@pedro.aquino.se/how-to-use-mcp-tools-on-claude-desktop-app-and-automate-your-daily-tasks-1c38e22bc4b0>

## Claude Desktop Setup for MCP 🖥️

1. Install Claude Desktop

```bash
# Assuming you're on macOS
brew install claude-desktop

# Or download from official website
https://claude.ai/desktop
```

3. Set up Datadog MCP:

```bash
# on mac is 
~/Library/Application\ Support/Claude/claude_desktop_config.json
````

```json
# change your claude config json by adding mcp
    "Datadog-MCP-Server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "datadog-api-client",
        "--with",
        "fastmcp",
        "--with",
        "icecream",
        "--with",
        "loguru",
        "--with",
        "python-dotenv",
        "fastmcp",
        "run",
        "/your-path/mcp-collection/datadog/main.py"
      ],
      "env": {
        "DD_API_KEY": "xxxx",
        "DD_APP_KEY": "xxx"
      }
    },
```

```bash 
# Install as MCP extension
cd datadog
task install-mcp
```

## 4. Verify Installation:

 
### In Claude chat desktop
 check datadog connection in claude

![setup claude](assets/config.png)

 you will see that
![alt text](./assets/config2.png)
```

## MCP Structure in This Project 📐

```python
# MCP Server setup
mcp = FastMCP(
    "Datadog-MCP-Server",
    dependencies=[
        "loguru",
        "icecream",
        "python-dotenv",
        "datadog-api-client",
    ],
)

# Tool definition
@mcp.tool()
def get_monitor_states():
    # Tool implementation

# Prompt definition
@mcp.prompt()
def analyze_error_logs():
    # Prompt implementation
```

## Security Considerations 🔒

- Store API keys in `.env`
- MCP runs in isolated environment
- Each tool has defined permissions
- Rate limiting is implemented

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
