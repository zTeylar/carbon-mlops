resource "aws_scheduler_schedule" "carbon_mlops_ingestion_scheduler" {
  name        = "carbon-mlops-ingestion-scheduler"
  description = "Scheduler for carbon ingestion Lambda function"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(30 minutes)"
  state               = "ENABLED"

  target {
    arn      = aws_lambda_function.carbon_ingestion.arn
    role_arn = aws_iam_role.scheduler_execution.arn
  }
}