
resource "aws_api_gateway_rest_api" "googleCivicREST_API" {
  name        = "googleCivicREST_API"
  description = "API to retrieve info from google's civic api"
}


resource "aws_api_gateway_resource" "governors" {
  parent_id   = aws_api_gateway_rest_api.googleCivicREST_API.root_resource_id
  path_part   = "governors"
  rest_api_id = aws_api_gateway_rest_api.googleCivicREST_API.id
}


resource "aws_api_gateway_method" "get" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.governors.id
  rest_api_id   = aws_api_gateway_rest_api.googleCivicREST_API.id
}


resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.googleCivicREST_API.id
  resource_id = aws_api_gateway_method.get.resource_id
  http_method = aws_api_gateway_method.get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_function.invoke_arn
}


resource "aws_api_gateway_deployment" "googleCivicREST_API" {
  depends_on = [
    aws_api_gateway_integration.lambda
  ]

  rest_api_id = aws_api_gateway_rest_api.googleCivicREST_API.id
  stage_name  = "dev"
}

output "base_url" {
  value = aws_api_gateway_deployment.googleCivicREST_API.invoke_url
}