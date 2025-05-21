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

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return_code = process.returncode
    return stdout.decode(), stderr.decode(), return_code


def talk_llm(question_llm: str) -> str:
    chat_completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional Kubernetes engineer. An expert at analysis Kubernetes resources and creating resources. During generation of Kubernetes resources, make sure to only generate the yaml file and nothing else. During analysis make sure that user's request has been fulfilled.",
            },
            {"role": "user", "content": question_llm},
        ],
    )

    return str(chat_completion.choices[0].message.content)


def create_file(filename: str, content: str):
    with open(filename, "w") as file:
        file.write(content)
    

@mcp.tool()
def create_k8s_resource(user_input: str):

    """
    This tool is responsible for creating any Kubernetes resource.

    Args:
        user_input: this includes the user's request to create a Kubernetes resource
        For example:
            'Can you create a deployment resource with following configurations:
                deployment-name: devs-deployment
                container-port: 80
                image: nginx:latest
                app-selector: devs-app'
    
    Returns:
        A string message indicating the result of the request: success confirmation with output, or failure with error details.
    """
    k8s_resource = talk_llm(user_input)

    # Confirm k8s_resource creation
    confirmation = talk_llm(
        f"""
        "Here is a user's request: {user_input}. And here is the YAML that was generated: {k8s_resource}.
        Please check if the YAML fully satisfies the request. If it does, return only the YAML file without any extra explanation and only YAML content with out ```yml at the start and ``` at the end.
        If not, update the YAML to fulfill the request."

        """
    )
    create_file("k8s-resources.yaml",f"{str(confirmation)}")
    output, err, return_code = execute_command(f"kubectl create -f k8s-resources.yaml")

    if return_code != 0:
        return f"Resource Creation Failed due to {err}"
    else:
        return f"Resource has been created successfully. {output}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
