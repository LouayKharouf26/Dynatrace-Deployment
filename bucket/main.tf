provider "aws" {
    region = var.region
}

resource "aws_s3_bucket" "state" {
  bucket = "${var.aws_account_id}-bucket-state-file-dynatrace"

  tags = {
    Environment = var.environment
  }
}
