/* Import the AWS CloudWatch Log Group resource */
resource "aws_cloudwatch_log_group" "carbon_ingestion_log_group" {

  name              = "/aws/lambda/${aws_lambda_function.carbon_ingestion.function_name}"
  retention_in_days = 14
  tags = {
    Project     = "carbon-mlops"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}


resource "aws_cloudwatch_metric_alarm" "carbon_ingestion_error_alarm" {
  alarm_name          = "carbon-mlops-ingestion-error-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 1800
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  dimensions = {
    FunctionName = aws_lambda_function.carbon_ingestion.function_name
  }
  alarm_description = "Alarm when the carbon ingestion Lambda function has errors"
}