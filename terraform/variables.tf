variable "region" {
  description = "The region to deploy to, if not set the default provider region is used."
}

variable "zone" {
  description = "The zone to deploy to, if not set the default provider zone is used."
}

variable "project_tag_name" {
  description = "The project to deploy to, if not set the default provider project is used."
  default     = ""
}
