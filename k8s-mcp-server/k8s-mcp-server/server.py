from kubernetes import client, config
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("k8s-mcp-server")


@mcp.tool()
def list_pod():
    """
    This tool returns all the pods across all the namespaces in the kubernetes cluster.

    Returns:
        String containing pod details including pod ip, pod namespace and pod name.
    """
    config.load_kube_config(config_file="/home/devjpt23/.kube/config")
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    pods_det = []
    for i in ret.items:
        pods_det.append(
            "%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)
        )
    return pods_det


def create_deployment_object(image: str, port: int, deployment_name: str, replicas:int):

    container = client.V1Container(
        name=deployment_name,
        image=image,
        ports=[client.V1ContainerPort(container_port=port)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "200Mi"},
            limits={"cpu": "500m", "memory": "500Mi"},
        ),
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
        spec=client.V1PodSpec(containers=[container]),
    )

    spec = client.V1DeploymentSpec(
        replicas, template=template, selector={"matchLabels": {"app": deployment_name}}
    )

    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=spec,
    )

    return deployment


def obj_to_deploy(api, deployment):
    api.create_namespaced_deployment(body=deployment, namespace="default")


@mcp.tool()
def create_deployment(image: str, port: int, deployment_name: str, replicas: int):
    """
    This tool creates deployment object on kubernetes cluster

    Args:
        image: name of the image that will run in the container
        port: port that is going to be exposed
        deployment_name: name of the deployment
        replicas: the amount of pods that should be backed by this deployment

        Example:
        create_deployment{
            "image":"nginx:latest",
            "port":80,
            "deployment_name":"devs-deployment",
            "replicas":3
        }
    Returns:
        A string message confirming that the deployment has been created successfully.
    """
    config.load_kube_config(config_file="/home/devjpt23/.kube/config")
    apps_v1 = client.AppsV1Api()

    deployment = create_deployment_object(image, port, deployment_name, replicas)
    obj_to_deploy(apps_v1, deployment)
    return f"{deployment_name} has been deployed sucessfully"
    


if __name__ == "__main__":
    mcp.run(transport="stdio")
