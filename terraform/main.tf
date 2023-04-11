provider "aws" {
  region = var.region
  # profile = var.profile
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

locals {
  common_tags = {
    project = var.project_tag_name
  }
}
resource "aws_s3_bucket" "gamification_bucket" {
  bucket = "gamification-bucket2023"
  tags = merge(
    local.common_tags,
    {
      Terraform   = "True"
      Environment = "Dev"
    },
  )
}

# resource "aws_s3_bucket_acl" "gamification_bucket_acl" {
#   bucket = aws_s3_bucket.gamification_bucket.id
#   acl = "private"
# }

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.gamification_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
        ]
        Effect = "Allow"
        Resource = "${aws_s3_bucket.gamification_bucket.arn}/*"
        Principal = "*"
      }
    ]
  })
}
