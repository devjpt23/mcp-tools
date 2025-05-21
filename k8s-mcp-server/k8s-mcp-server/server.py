import os
import subprocess
from groq import Groq
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from kubernetes.client import api_client
from kubernetes import client, config, dynamic

load_dotenv()

mcp = FastMCP("k8s-mcp-server")

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@mcp.tool()
def get_resource_template(resource: str):
    """
    Retrieve the YAML template structure for a specified Kubernetes resource.

    Args:
        resource (str): The name of the Kubernetes resource to explain (e.g., 'deployment', 'service').
    
    Returns:
        str: The detailed structure and fields of the resource, as provided by 'kubectl explain --recursive'.
    """
    cmd = ["kubectl", "explain", resource, "--recursive"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout

if __name__ == "__main__":
    mcp.run(transport="stdio")
