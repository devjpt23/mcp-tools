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
    Retrieve the YAML template structure for a specified Kubernetes resource using 'kubectl explain --recursive'.

    Parameters:
        resource (str): The name of the Kubernetes resource to explain (e.g., 'deployment', 'service', 'pod').

    Returns:
        str: The detailed structure and fields of the resource, as provided by 'kubectl explain --recursive'.

    Example:
        Input:
            can you create a template for a pod with name mypod with image myimage
        Output:
            apiVersion: v1
            kind: Pod
            metadata:
              name: mypod
            spec:
              containers:
              - name: mycontainer
                image: myimage
            ...

        Note:
        Do not save the yaml file into yaml file, just display the content.
    """
    cmd = ["kubectl", "explain", resource, "--recursive"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout

@mcp.tool()
def save_yaml(response: str, filename: str = "resource.yaml"):
    """
    Save the provided YAML or text response to a file on the host where the MCP server is running.

    Parameters:
        response (str): The content to be saved (typically YAML or text data).
        filename (str, optional): The name of the file to save the response to. Defaults to 'resource.yaml'.

    Returns:
        str: A confirmation message indicating that the response has been successfully saved to the specified file.

    Example:
        >>> yaml_content = (
        ...     'apiVersion: v1\n'
        ...     'kind: Pod\n'
        ...     'metadata:\n'
        ...     '  name: mypod\n'
        ...     'spec:\n'
        ...     '  containers:\n'
        ...     '  - name: mycontainer\n'
        ...     '    image: myimage\n'
        ... )
        >>> save_yaml(yaml_content, filename="mypod.yaml")
        'File mypod.yaml has been created with the resource!'
    """
    with open(f"resources/{filename}", "w") as f:
        f.write(response)
    
    return f'File {filename} has been created with the resource!'

@mcp.tool()
def execute_yaml(filename):
    """
    Apply a Kubernetes resource YAML file using 'kubectl create -f'.

    Parameters:
        filename (str): The name of the YAML file (located in the 'resources' directory) to be applied to the Kubernetes cluster.

    Returns:
        str: The output from the 'kubectl create' command, indicating the result of the resource creation.
    """
    cmd = ["kubectl", "create","-f", f"resources/{filename}"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout

if __name__ == "__main__":
    mcp.run(transport="stdio")