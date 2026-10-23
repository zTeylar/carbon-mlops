terraform {
  backend "s3" {
    bucket       = "carbon-mlops-tfstate-c4426dce979d16e082f3039dd9"
    key          = "terraform.tfstate"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }
}