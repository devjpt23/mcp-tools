import json
import yaml
from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
from kubernetes.client import ApiClient
from kubernetes.dynamic.exceptions import ConflictError, DynamicApiError


mcp = FastMCP("k8s-mcp-server")


def get_schema_raw_and_definition(resource_kind: str):
    config.load_kube_config(config_file="/home/devjpt23/.kube/config")
    api_client = client.ApiClient()

    response = api_client.call_api(
        "/openapi/v2",
        "GET",
        response_type="str",
        auth_settings=["BearerToken"],
        _preload_content=False,
    )

    schema_raw = json.loads(response[0].data)

    definition_key = None

    for key in schema_raw["definitions"].keys():
        if key.endswith(resource_kind):
            print(key)
            definition_key = key
            break

    definition = schema_raw["definitions"][definition_key]
    description = definition["description"]
    return (definition, schema_raw["definitions"], description)


def explain_fields(schema, definitions, indent=0):
    properties = schema.get("properties", {})
    lines = []
    for name, fields in properties.items():
        lines.append(" " * indent + f"{name}: {fields.get('type','object')}")
        ref = fields.get("$ref")
        if ref:
            ref_key = ref.split("/")[-1]
            lines.append(explain_fields(definitions[ref_key], definitions, indent + 2))
        elif fields.get("type") == "array" and "items" in fields:
            item_ref = fields["items"].get("$ref")
            if item_ref:
                ref_key = item_ref.split("/")[-1]
                lines.append(
                    explain_fields(definitions[ref_key], definitions, indent + 2)
                )
    return "\n".join(lines)


@mcp.tool()
def get_resource_template(resource_kind: str):
    """
    Generate a detailed explanation of a Kubernetes resource, including its description and schema fields.

    Args:
        resource_kind (str): The kind of Kubernetes resource to explain (e.g., 'Pod', 'Deployment').

        NOTE: THE RESOURCE KIND STRING MUST BE IN CAMEL CASE FOR EXAMPLE: ClusterRoleBinding and not clusterrolebinding.

    Returns:
        str: A formatted string containing the resource description and schema fields.
    """
    definition, definitions, description = get_schema_raw_and_definition(resource_kind)
    fields_explanation = explain_fields(definition, definitions)

    return f"""
    DESCRIPTION:
        {description}
        
    FIELDS:
        {fields_explanation}
"""


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

    return f"File {filename} has been created with the resource!"


def parse_yaml(filename: str):
    kind = ""
    apiVersion = ""
    with open(f"resources/{filename}") as stream:
        try:
            data = yaml.safe_load(stream)
            for key, value in data.items():
                if key == "kind":
                    kind += value

                if key == "apiVersion":
                    apiVersion += value

        except yaml.YAMLError as exc:
            print(exc)

    return kind, apiVersion, data


@mcp.tool()
def execute_yaml(filename: str, namespace: str) -> str:

    config.load_kube_config(config_file="/home/devjpt23/.kube/config")
    api_client = ApiClient()
    dyn_client = DynamicClient(api_client)

    kind, apiVersion, manifest = parse_yaml(filename)
    resource = dyn_client.resources.get(
        api_version=apiVersion,
        kind=kind,
    )

    try:
        resource.create(body=manifest, namespace=namespace)
        return f"{kind} has been created!"
    except ConflictError as e:
        return f"Failed to create resource, resource already exists.{e.body}"
    except DynamicApiError as e:
        return f"Failed to create resource: {e.body}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
