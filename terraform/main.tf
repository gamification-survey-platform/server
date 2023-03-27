provider "aws" {
  region = var.region
}

locals {
  common_tags = {
    Project = var.project_tag_name
  }
}
resource "aws_s3_bucket" "static_content" {
  bucket = "artifacts_file"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = merge(
    local.common_tags,
    {
      Terraform   = "True"
      Environment = "Dev"
    },
  )
}

# resource "aws_s3_bucket" "bucket_name" {
#   bucket = "my-bucket-name"
#   acl    = "private"

#   tags = {
#     Terraform   = "True"
#     Environment = "Dev"
#   }
# }
