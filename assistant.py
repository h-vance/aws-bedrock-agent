import boto3
import json
import logging
import os
from botocore.exceptions import ClientError

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Clients
bedrock = boto3.client("bedrock-runtime")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

# --- Reliability Tool Definitions ---

def get_service_logs(service_name: str, lines: int = 50):
    """Simulates fetching logs for a specific service."""
    logger.info(f"Tool Call: Fetching {lines} lines for {service_name}")
    return f"MOCK LOG DATA for {service_name}: [ERROR] 500 Internal Server Error at 2026-05-07T14:32:10Z"

def restart_service(service_name: str):
    """Simulates a service restart remediation action."""
    logger.warning(f"Tool Call: RESTARTING service {service_name}")
    return f"Service {service_name} restart initiated successfully."

def scale_up(resource_name: str, increment: int = 1):
    """Simulates scaling up a resource (e.g., ASG or ECS Service)."""
    logger.info(f"Tool Call: SCALING {resource_name} by {increment} units")
    return f"Scale up for {resource_name} by {increment} units complete."

TOOLS = [
    {
        "toolSpec": {
            "name": "get_service_logs",
            "description": "Fetch logs for a service to triage an incident.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Name of the service to query"},
                        "lines": {"type": "integer", "description": "Number of log lines to retrieve"}
                    },
                    "required": ["service_name"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "restart_service",
            "description": "Restart a service as a remediation step.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Name of the service to restart"}
                    },
                    "required": ["service_name"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "scale_up",
            "description": "Increase capacity for a resource.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "resource_name": {"type": "string", "description": "Name of the resource to scale"},
                        "increment": {"type": "integer", "description": "Number of units to add"}
                    },
                    "required": ["resource_name"]
                }
            }
        }
    }
]

# --- Orchestrator Logic ---

def execute_tool(name, args):
    if name == "get_service_logs":
        return get_service_logs(**args)
    elif name == "restart_service":
        return restart_service(**args)
    elif name == "scale_up":
        return scale_up(**args)
    return "Unknown tool."

def run_agent_loop(event_context):
    system_prompt = """You are an Elite Production Reliability Ops Agent. 
    You receive CloudWatch Alarms and must triage and remediate them using the provided tools.
    1. Analyze the alarm details.
    2. Use 'get_service_logs' to investigate if needed.
    3. Use 'restart_service' or 'scale_up' to fix the issue based on your analysis.
    4. Provide a concise summary of your actions."""

    messages = [{"role": "user", "content": [{"text": f"ALARM CONTEXT: {json.dumps(event_context)}"}]}]
    
    # Simple loop for multi-turn tool calling
    for _ in range(5):
        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": system_prompt}],
            messages=messages,
            toolConfig={"tools": TOOLS}
        )
        
        output_msg = response["output"]["message"]
        messages.append(output_msg)
        
        # Check if model wants to use a tool
        tool_requests = [c for c in output_msg["content"] if "toolUse" in c]
        if not tool_requests:
            return output_msg["content"][0]["text"]

        # Handle tool results
        tool_results_content = []
        for req in tool_requests:
            tool_use = req["toolUse"]
            tool_name = tool_use["name"]
            tool_args = tool_use["input"]
            tool_id = tool_use["toolUseId"]
            
            result_text = execute_tool(tool_name, tool_args)
            
            tool_results_content.append({
                "toolResult": {
                    "toolUseId": tool_id,
                    "content": [{"text": str(result_text)}]
                }
            })
        
        messages.append({"role": "user", "content": tool_results_content})

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Determine if this is an EventBridge Alarm or manual test
        alarm_detail = event.get("detail", event)
        result = run_agent_loop(alarm_detail)
        
        logger.info(f"Remediation Result: {result}")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "Success", "remediation_summary": result})
        }
    except Exception as e:
        logger.error(f"Error in agent: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "Error", "message": str(e)})
        }
