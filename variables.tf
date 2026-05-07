variable "aws_region" {
  description = "The AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "bedrock-ops-agent"
}

variable "environment" {
  description = "The deployment environment (e.g., prod, dev)."
  type        = string
  default     = "prod"
}

variable "bedrock_model_id" {
  description = "The Bedrock model ID to use."
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs."
  type        = number
  default     = 14
}
