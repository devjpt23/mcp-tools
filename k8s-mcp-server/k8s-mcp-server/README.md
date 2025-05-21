# AI-Driven Kubernetes Resource Manager

## Overview

This project provides an AI-powered interface for creating and managing Kubernetes resources using natural language. It leverages large language models (LLMs) from Groq, the Modular Command Protocol (MCP) framework, and the Kubernetes Python client to allow users to describe the resources they want, automatically generate the corresponding YAML, validate it, and apply it to a Kubernetes cluster.

The repository consists of two main components:
- **Server**: Exposes an MCP tool for Kubernetes resource creation, powered by an LLM.
- **Client**: Demonstrates how to interact with the server using an LLM agent and MCP tools.

## Features

- **Natural Language to Kubernetes YAML**: Describe any Kubernetes resource in plain English and have it created automatically.
- **LLM-Powered Validation**: Generated YAML is validated by the LLM to ensure it matches the user's intent.
- **Automated Application**: Validated YAML is applied directly to your Kubernetes cluster.
- **Extensible Agent Interface**: The client uses LangChain and Groq to create an agent that can invoke MCP tools and process complex instructions.

## How it Works

1. **Server**
    - Exposes a tool (`create_k8s_resource`) via MCP.
    - Receives a user request (in natural language) to create a Kubernetes resource.
    - Uses Groq's Llama model to generate the appropriate Kubernetes YAML.
    - Asks the LLM to validate that the YAML matches the request, updating it if necessary.
    - Writes the YAML to a file and applies it to the cluster using `kubectl`.

2. **Client**
    - Connects to the server using MCP over stdio.
    - Loads available tools and creates a LangChain agent with Groq's LLM.
    - Sends user instructions (e.g., "create a deployment with nginx:latest, port 80, 3 replicas") to the agent.
    - The agent invokes the server's tool, and the resource is created in the cluster.

## Example Usage

- **Create a Deployment**
    - User instruction: _"Create a deployment named 'devs-deployment' with image 'nginx:latest', running on port 80, with 3 replicas."_
    - The system generates and applies the following YAML:

      ```yaml
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: devs-deployment
      spec:
        replicas: 3
        selector:
          matchLabels:
            app: devs-deployment
        template:
          metadata:
            labels:
              app: devs-deployment
          spec:
            containers:
            - name: devs-container
              image: nginx:latest
              ports:
              - containerPort: 80
      ```

## Setup

### Prerequisites
- Python 3.12+
- Access to a Kubernetes cluster (with `kubectl` configured)
- Groq API key (for LLM access)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt  # or use pyproject.toml with your preferred tool
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
- `server.py`: MCP server exposing the Kubernetes resource creation tool.
- `client.py`: Example client/agent that interacts with the server.
- `create_resource.py`: Standalone script for resource creation (optional usage).
- `k8s-resources.yaml`: Example of generated resource YAML.
- `pyproject.toml`: Project dependencies and metadata.

## License

MIT License