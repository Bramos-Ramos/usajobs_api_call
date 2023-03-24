terraform {

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
