terraform {

}

resource "aws_ecs_task_definition" "us-jobs-task-definition" {
  family                = "us-jobs-task"
  container_definitions = jsonencode([{
    name           = "us-jobs-container"
    image          = "public.ecr.aws/n9v1m6p2/tasman-test:latest"
    memory         = 256
    cpu            = 256
    portMappings   = [{
      containerPort = 8080
      hostPort      = 80
      protocol      = "tcp"
    }]
  }])
}

resource "aws_iam_role" "ecs-service" {
  name = "ecs-service-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
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
  name = "us-job-cluster"
}

resource "aws_ecs_service" "us-jobs-service" {
  name             = "us-jobs-service"
  cluster          = aws_ecs_cluster.us-jobs-cluster.id
  task_definition  = aws_ecs_task_definition.us-jobs-task-definition.arn
  desired_count    = 1
  depends_on       = [aws_ecs_task_definition.us-jobs-task-definition]
}
