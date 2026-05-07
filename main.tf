terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Lambda Source Code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "assistant.py"
  output_path = "assistant.zip"
}

# SQS Dead Letter Queue
resource "aws_sqs_queue" "lambda_dlq" {
  name = "${var.project_name}-dlq"
}

# CloudWatch Log Group with defined retention
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.bedrock_agent.function_name}"
  retention_in_days = var.log_retention_days
}

# Bedrock Orchestrator Lambda
resource "aws_lambda_function" "bedrock_agent" {
  filename         = "assistant.zip"
  function_name    = var.project_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "assistant.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 60 # Increased for Bedrock response time

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }

  environment {
    variables = {
      BEDROCK_MODEL_ID = var.bedrock_model_id
      LOG_LEVEL        = "INFO"
    }
  }
}

# EventBridge Rule for Operational Alarms
resource "aws_cloudwatch_event_rule" "operational_alarms" {
  name        = "${var.project_name}-alarms"
  description = "Triggers the Bedrock Agent on CloudWatch Alarm state changes."

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      state = {
        value = ["ALARM"]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.operational_alarms.name
  target_id = "TriggerBedrockAgent"
  arn       = aws_lambda_function.bedrock_agent.arn
}
