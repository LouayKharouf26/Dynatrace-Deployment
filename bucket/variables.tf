variable "region" {
  type        = string
  description = "AWS Region"
  default     = "eu-west-3"
}

variable "aws_account_id" {
  type        = string
  description = "AWS Account ID"
}

variable "environment" {
  type        = string
  description = "AWS Environment"
  default     = "dev"
}