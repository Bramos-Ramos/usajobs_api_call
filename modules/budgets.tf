terraform {
}

resource "aws_budgets_budget" "budget-for-test" {
  name          = "monthly-budget"
  budget_type   = "COST"
  limit_amount  = "10.0"
  limit_unit    = "USD"
  time_unit     = "MONTHLY"
  time_period_start = "2023-03-21_00:01"
}
