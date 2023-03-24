terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


module "modules" {
  source = "./modules"
}
