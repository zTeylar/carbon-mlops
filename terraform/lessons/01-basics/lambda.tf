resource "aws_lambda_function" "carbon_ingestion" {
  function_name = "carbon-mlops-ingestion"
  role          = aws_iam_role.lambda_execution.arn

  filename         = "${path.module}/../../../build/carbon-mlops-lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../../../build/carbon-mlops-lambda.zip")

  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      CARBON_RAW_BUCKET = aws_s3_bucket.raw_data.bucket
    }
  }

  tags = {
    Project     = "carbon-mlops"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}