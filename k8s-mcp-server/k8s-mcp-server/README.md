# Kubernetes MCP Server & Client

## Overview

This project provides a modular interface for creating and managing Kubernetes resources using MCP (Modular Command Protocol) tools. It exposes a server with tools for retrieving resource templates, saving YAML files, and applying them to a Kubernetes cluster. The client demonstrates how to interact with these tools, optionally leveraging an LLM (Groq) to generate resource YAML from natural language instructions.

## Features

- **Resource Template Retrieval**: Get the YAML structure for any Kubernetes resource using `kubectl explain --recursive`.
- **YAML File Management**: Save generated or provided YAML to the server's filesystem.
- **Automated Application**: Apply saved YAML files directly to your Kubernetes cluster using `kubectl create -f`.
- **LLM Integration (Client Side)**: The client can use Groq's Llama model to generate Kubernetes YAML from natural language, but the server itself does not generate YAML from prompts.

## How it Works

### Server
- Exposes three MCP tools:
  - `get_resource_template`: Returns the YAML structure for a given Kubernetes resource (e.g., Deployment, Service, Pod).
  - `save_yaml`: Saves provided YAML/text to a file in the `resources/` directory.
  - `execute_yaml`: Applies a YAML file from the `resources/` directory to the Kubernetes cluster.
- Does **not** generate YAML from natural language; it only provides templates, saves, and applies YAML.

### Client
- Connects to the server using MCP over stdio.
- Loads available tools and can use an LLM (Groq) to generate YAML from user instructions.
- Demonstrates a workflow: generate YAML (via LLM), save it to the server, and apply it to the cluster.

## Example Usage

- **Get a Resource Template**
  - User: _"Show me the template for a Deployment"_
  - Tool: `get_resource_template('deployment')`

- **Create and Apply a Deployment**
  - User: _"Create a deployment named 'devs-deployment' with image 'nginx:latest', running on port 80, with 3 replicas."_
  - Client uses LLM to generate YAML, then:
    1. `save_yaml(yaml_content, filename="devs-deployment.yaml")`
    2. `execute_yaml(filename="devs-deployment.yaml")`

## Setup

### Prerequisites
- Python 3.12+
- Access to a Kubernetes cluster (with `kubectl` configured)
- Groq API key (for LLM-powered YAML generation in the client)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variable:
   - Create a `.env` file with:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     ```

### Running the Server
```bash
python server.py
```

### Running the Client (Example Agent)
```bash
python client.py
```

## Project Structure
- `server.py`: MCP server exposing tools for resource template retrieval, YAML saving, and application.
- `client.py`: Example client/agent that interacts with the server and can use an LLM to generate YAML.
- `resources/`: Directory where YAML files are saved and read from.
- `pyproject.toml`/`requirements.txt`: Project dependencies and metadata.

## License

MIT License