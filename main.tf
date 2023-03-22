terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
        }
    }

}
provider "aws" {
  region = "eu-west-2"
}

resource "aws_budgets_budget" "budget-for-test" {
    name = "monthly-budget"
    budget_type = "COST"
    limit_amount = "10.0"
    limit_unit = "USD"
    time_unit = "MONTHLY"
    time_period_start = "2023-03-21_00:01"
  
}


resource "aws_ecs_task_definition" "us-jobs-task-definition" {
  family                   = "us-jobs-task"
  container_definitions    = jsonencode([{
    name                    = "us-jobs-container"
    image                   = "public.ecr.aws/n9v1m6p2/tasman-test:latest"
    memory                  = 256
    cpu                     = 256
    portMappings            = [{
      containerPort         = 8080
      hostPort              = 80
      protocol              = "tcp"
    }]
  }])
}

resource "aws_iam_role" "ecs-service" {
  name = "ecs-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs-service" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRole"
  role       = aws_iam_role.ecs-service.name
}


resource "aws_ecs_cluster" "us-jobs-cluster" {
  name                     = "us-job-cluster"
}

resource "aws_ecs_service" "us-jobs-service" {
  name                     = "us-jobs-service"
  cluster                  = aws_ecs_cluster.us-jobs-cluster.id
  task_definition          = aws_ecs_task_definition.us-jobs-task-definition.arn
  desired_count            = 1
  depends_on               = [aws_ecs_task_definition.us-jobs-task-definition]
}


resource "aws_cloudwatch_event_rule" "us-jobs-rule" {
  name                = "us-jobs-rule"
  description         = "Trigger my-service daily 5 minutes"
  schedule_expression = "rate(5 minutes)"
}


resource "aws_cloudwatch_event_target" "us-jobs-target" {
  rule      = aws_cloudwatch_event_rule.us-jobs-rule.name
  arn       = aws_ecs_cluster.us-jobs-cluster.arn  
  target_id = "ecs-target"
  role_arn  = aws_iam_role.ecs-service.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.us-jobs-task-definition.arn
    task_count          = 1
  }
}
