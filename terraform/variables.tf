variable "region" {
  description = "The region to deploy to, if not set the default provider region is used."
}

variable "zone" {
  description = "The zone to deploy to, if not set the default provider zone is used."
}

variable "project_tag_name" {
  description = "The project to deploy to, if not set the default provider project is used."
}

variable "aws_access_key" {
  description = "The AWS access key to use for the provider."
}

variable "aws_secret_key" {
  description = "The AWS secret key to use for the provider."
}
