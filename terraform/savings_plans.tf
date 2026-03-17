# AWS Savings Plans — Deepak Vaida
# Compute Savings Plan: ~$70,000/year saved at MBFS

# Note: Savings Plans are purchased via AWS Console or CLI
# This Terraform documents the configuration for tracking purposes

# AWS Budget Alert — notify at 80% and 100% of monthly budget
resource "aws_budgets_budget" "monthly" {
  name         = "mbfs-monthly-aws-budget"
  budget_type  = "COST"
  limit_amount = "50000"  # $50K/month budget
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name = "Service"
    values = ["Amazon Elastic Compute Cloud - Compute", "Amazon Elastic Kubernetes Service"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["deepakv2353@gmail.com"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["deepakv2353@gmail.com"]
  }
}

# Cost Anomaly Detection
resource "aws_ce_anomaly_monitor" "main" {
  name              = "mbfs-cost-anomaly-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "main" {
  name      = "mbfs-cost-anomaly-alert"
  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["1000"]  # Alert if anomaly > $1000
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }
  frequency = "DAILY"
  monitor_arn_list = [aws_ce_anomaly_monitor.main.arn]
  subscriber {
    address = "deepakv2353@gmail.com"
    type    = "EMAIL"
  }
}
