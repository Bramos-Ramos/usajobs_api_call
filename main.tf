terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


module "provider" {
  source = "./modules"
}

module "budgets" {
  source = "./modules"
}

module "ecs" {
  source = "./modules"
}

module "cloudwatch" {
  source = "./modules"
}
