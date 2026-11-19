resource "aws_iam_role" "lambda_execution" {
  name = "carbon-mlops-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_upload_policy" {
  name = "carbon-mlops-lambda-upload-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.raw_data.arn}/carbon-intensity/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_upload_policy_attachment" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_upload_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


resource "aws_iam_role" "scheduler_execution" {
  name = "carbon-mlops-scheduler-execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "sts:AssumeRole",
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
    }]
  })
}


resource "aws_iam_role_policy" "scheduler_execution_policy" {
  name = "carbon-mlops-scheduler-execution-policy"
  role = aws_iam_role.scheduler_execution.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction"
        ],
        Resource = aws_lambda_function.carbon_ingestion.arn
      }
    ]
  })
}


moved {
  from = aws_iam_role.lambda_execution_replacement
  to   = aws_iam_role.lambda_execution
}

moved {
  from = aws_iam_policy.lambda_upload_policy_replacement
  to   = aws_iam_policy.lambda_upload_policy
}

moved {
  from = aws_iam_role_policy_attachment.lambda_upload_policy_replacement_attachment
  to   = aws_iam_role_policy_attachment.lambda_upload_policy_attachment
}

moved {
  from = aws_iam_role_policy_attachment.lambda_basic_execution_replacement
  to   = aws_iam_role_policy_attachment.lambda_basic_execution
}