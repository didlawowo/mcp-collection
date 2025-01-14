import mcp.server.stdio
import mcp.types as types
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
import os
import json
from loguru import logger
from fastmcp import FastMCP
from fastmcp.prompts.base import UserMessage, AssistantMessage
from typing import Generator
from datadog_api_client.v2.models import LogsListResponse
from icecream import ic
from dotenv import load_dotenv
from datadog_api_client.v1.api.monitors_api import MonitorsApi


load_dotenv()

mcp = FastMCP(
    "Datadog-MCP-Server",
    dependencies=[
        "loguru",
        "icecream",
        "python-dotenv",
        "datadog-api-client",
    ],
)


def fetch_logs_paginated(
    api_instance: LogsApi, query_params: dict, max_results: int = 1000
) -> Generator[LogsListResponse, None, None]:
    """Fetch logs with pagination support."""
    current_page = 0
    total_logs = 0

    while total_logs < max_results:
        query_params["page"] = {
            "limit": min(100, max_results - total_logs),
            "cursor": current_page,
        }
        response = api_instance.list_logs(body=query_params)

        if not response.data:
            break

        yield response
        total_logs += len(response.data)
        current_page += 1


def extract_tag_value(tags: list, prefix: str) -> str:
    """Helper pour extraire une valeur de tag avec un préfixe donné"""
    for tag in tags:
        if tag.startswith(prefix):
            return tag.split(":", 1)[1]
    return None


@mcp.tool()
def get_monitor_states(
    name: str,
    timeframe: int = 1,
) -> list[types.TextContent]:
    """
    Get monitor states for a specific monitor with retry mechanism

    Args:
        name: monitor name
        timeframe: Hours to look back (default: 1)
    """

    def serialize_monitor(monitor) -> dict:
        """Helper to serialize monitor data"""
        return {
            "id": str(monitor.id),
            "name": monitor.name,
            "query": monitor.query,
            "status": str(monitor.overall_state),
            "last_triggered": monitor.last_triggered_ts
            if hasattr(monitor, "last_triggered_ts")
            else None,
            "message": monitor.message if hasattr(monitor, "message") else None,
            "type": monitor.type if hasattr(monitor, "type") else None,
            "created": str(monitor.created) if hasattr(monitor, "created") else None,
            "modified": str(monitor.modified) if hasattr(monitor, "modified") else None,
        }

    def fetch_monitors():
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)

            # Get all monitors and filter by name
            response = monitors_api.list_monitors(
                page_size=100  # 👈 Increased page size
            )

            # Filter monitors by name (case insensitive)
            monitor_details = []
            for monitor in response:
                if name.lower() in monitor.name.lower():
                    monitor_details.append(monitor)

            return monitor_details

    try:
        configuration = Configuration()
        api_key = os.getenv("DD_API_KEY")
        app_key = os.getenv("DD_APP_KEY")

        if not api_key or not app_key:
            return [
                types.TextContent(
                    type="text", text="Error: Missing Datadog API credentials"
                )
            ]

        configuration.api_key["DD-API-KEY"] = api_key
        configuration.api_key["DD-APPLICATION-KEY"] = app_key
        configuration.server_variables["site"] = "datadoghq.eu"

        monitors = fetch_monitors()

        if not monitors:
            return [
                types.TextContent(
                    type="text", text=f"No monitors found with name containing '{name}'"
                )
            ]

        # Serialize monitors
        monitor_states = [serialize_monitor(monitor) for monitor in monitors]

        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    monitor_states, indent=2, default=str
                ),  # 👈 Added default serializer
            )
        ]

    except ValueError as ve:
        return [types.TextContent(type="text", text=str(ve))]
    except Exception as e:
        logger.error(f"Error fetching monitor states: {str(e)}")
        return [
            types.TextContent(
                type="text", text=f"Error fetching monitor states: {str(e)}"
            )
        ]


@mcp.tool()
def get_k8s_logs(
    cluster: str, timeframe: int = 5, namespace: str = None
) -> list[types.TextContent]:
    try:
        configuration = Configuration()
        api_key = os.getenv("DD_API_KEY")
        app_key = os.getenv("DD_APP_KEY")

        configuration.server_variables["site"] = "datadoghq.eu"

        configuration.api_key["DD-API-KEY"] = api_key
        configuration.api_key["DD-APPLICATION-KEY"] = app_key
        with ApiClient(configuration) as api_client:
            api_instance = LogsApi(api_client)

            # Construction d'une requête plus précise pour les erreurs
            query_components = [
                # "source:kubernetes",
                f"kube_cluster_name:{cluster}",
                "status:error OR level:error OR severity:error",  # 👈 Filtre des erreurs
            ]

            if namespace:
                query_components.append(f"kube_namespace:{namespace}")

            query = " AND ".join(query_components)

            response = api_instance.list_logs(
                body={
                    "filter": {
                        "query": query,
                        "from": f"now-{timeframe}h",  # 👈 Timeframe dynamique
                        "to": "now",
                    },
                    "sort": "-timestamp",  # Plus récent d'abord
                    "page": {
                        "limit": 100,  # Augmenté pour voir plus d'erreurs
                    },
                }
            )

            # Formatage plus pertinent de la réponse
            ic(f"Query: {query}")  # 👈 Log de la requête
            # ic(f"Response: {response}")  # 👈 Log de la réponse brute

            logs_data = response.to_dict()
            # ic(f"Logs data: {logs_data}")  # 👈 Log des données
            formatted_logs = []

            for log in logs_data.get("data", []):
                attributes = log.get("attributes", {})
                ic(attributes)
                formatted_logs.append(
                    {
                        "timestamp": attributes.get("timestamp"),
                        "host": attributes.get("host"),
                        "service": attributes.get("service"),
                        "pod_name": extract_tag_value(
                            attributes.get("tags", []), "pod_name:"
                        ),
                        "namespace": extract_tag_value(
                            attributes.get("tags", []), "kube_namespace:"
                        ),
                        "container_name": extract_tag_value(
                            attributes.get("tags", []), "kube_container_name:"
                        ),
                        "message": attributes.get("message"),
                        "status": attributes.get("status"),
                    }
                )

            return [
                types.TextContent(
                    type="text", text=json.dumps(formatted_logs, indent=2)
                )
            ]

    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


@mcp.prompt()
def analyze_monitors_data(name: str, timeframe: int = 3) -> list:
    """
    Analyze monitor data for a specific monitor.
    Parameters:
        name (str): The name of the monitor to analyze
        timeframe (int): Hours to look back for data
    Returns:
        list: Structured monitor analysis
    """
    try:
        monitor_data = get_monitor_states(name=name, timeframe=timeframe)
        if not monitor_data:
            return [
                AssistantMessage(
                    f"No monitor data found for '{name}' in the last {timeframe} hours."
                )
            ]
        # Format the response more naturally
        messages = [
            UserMessage(f"Monitor Analysis for '{name}' (last {timeframe} hours):")
        ]
        for data in monitor_data:
            messages.append(
                AssistantMessage(
                    f"Monitor State: {data['state']}, Timestamp: {data['timestamp']}"
                )
            )
        return messages
    except Exception as e:
        logger.error(f"Error analyzing monitor data: {str(e)}")
        return [AssistantMessage(f"Error: {str(e)}")]


@mcp.prompt()
def analyze_error_logs(
    cluster: str = "rke2", timeframe: int = 3, namespace: str = None
) -> list:
    """
    Analyze error logs from a Kubernetes cluster.

    Parameters:
        cluster (str): The cluster name to analyze
        timeframe (int): Hours to look back for errors
        namespace (str): Optional namespace filter

    Returns:
        list: Structured error analysis
    """
    logs = get_k8s_logs(cluster=cluster, namespace=namespace, timeframe=timeframe)

    if not logs:
        return [
            AssistantMessage(
                f"No error logs found for cluster '{cluster}' in the last {timeframe} hours."
            )
        ]

    # Format the response more naturally
    messages = [
        UserMessage(f"Error Analysis for cluster '{cluster}' (last {timeframe} hours):")
    ]

    try:
        log_data = json.loads(logs[0].text)
        if not log_data:
            messages.append(
                AssistantMessage("No errors found in the specified timeframe.")
            )
        else:
            # Group errors by service for better analysis
            errors_by_service = {}
            for log in log_data:
                service = log.get("service", "unknown")
                if service not in errors_by_service:
                    errors_by_service[service] = []
                errors_by_service[service].append(log)

            for service, errors in errors_by_service.items():
                messages.append(
                    AssistantMessage(
                        f"Service {service}: Found {len(errors)} errors\n"
                        + f"Most recent error: {errors[0].get('error_message', 'No message')}"
                    )
                )
    except json.JSONDecodeError:
        messages.append(AssistantMessage("Error parsing log data."))

    return messages
