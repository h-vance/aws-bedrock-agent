#!/bin/bash

# Mock CloudWatch Alarm State Change Event
MOCK_EVENT='{
  "version": "0",
  "id": "7bf73129-1428-4cd3-a780-95db273d1602",
  "detail-type": "CloudWatch Alarm State Change",
  "source": "aws.cloudwatch",
  "account": "123456789012",
  "time": "2026-05-07T14:30:00Z",
  "region": "us-east-1",
  "resources": ["arn:aws:cloudwatch:us-east-1:123456789012:alarm:High-CPU-Usage-Web-Tier"],
  "detail": {
    "alarmName": "High-CPU-Usage-Web-Tier",
    "state": {
      "value": "ALARM",
      "reason": "Threshold Crossed: 1 out of the last 1 datapoints [95.0 (07/05/26 14:29:00)] was greater than or equal to the threshold (90.0).",
      "reasonData": "{\"version\":\"1.0\",\"query_executions\":[{\"id\":\"e1\",\"query\":\"SELECT AVG(CPUUtilization) FROM AWS/ECS WHERE ServiceName = '\''web-service'\''\"}]}"
    },
    "previousState": {
      "value": "OK",
      "reason": "Threshold Crossed: no datapoints were greater than or equal to the threshold (90.0)."
    }
  }
}'

echo "🚀 Simulating CloudWatch Alarm: High-CPU-Usage-Web-Tier..."

# In a local dev environment, this just prints the payload or attempts to invoke if AWS CLI is configured
# For portfolio demonstration, we'll output the payload to a local file that the user can use with aws lambda invoke
echo "$MOCK_EVENT" > scripts/mock-event.json

echo "✅ Mock event generated at scripts/mock-event.json"
echo "To test your Lambda, run:"
echo "aws lambda invoke --function-name bedrock-ops-agent --payload file://scripts/mock-event.json response.json"
echo "cat response.json | jq"
