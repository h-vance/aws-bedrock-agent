# AWS Bedrock Infrastructure Agent

Autonomous AI orchestration for automated cloud infrastructure management and self-healing operations.

## Architecture
This project leverages Amazon Bedrock and AWS Lambda to create an autonomous agent capable of monitoring infrastructure health and executing remediation workflows.

## Capabilities
- **Automated Triage**: Uses LLMs to analyze CloudWatch logs and identify root causes of failures.
- **Self-Healing**: Executes predefined Lambda functions to restart services or rotate credentials.
- **Natural Language Ops**: Provides a chat interface for querying infrastructure state and performing manual overrides.

## Deployment
- **Model**: Anthropic Claude 3 (via Bedrock)
- **Compute**: AWS Lambda (Python 3.11)
- **Integration**: EventBridge, CloudWatch, SNS
