resource "aws_iam_role" "lambda_execution" {
  name = "carbon-mlops_lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}


resource "aws_iam_policy" "lambda_upload_policy" {
  name = "carbon-mlops_lambda_upload_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.raw_data.arn}/carbon-intensity/*"
      }
    ]
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