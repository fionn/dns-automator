variable "region" {
  type    = string
  default = "ap-southeast-1"
}

variable "profile" {
  type        = string
  default     = "default"
  description = "aws-cli profile to use for deployment"
}

variable "pgp_key" {
  type        = string
  default     = "keybase:fionn"
  description = "Used to encrypt the secret access key"
}

variable "path" {
  type        = string
  default     = "/application/dns-automator/"
  description = "Namespace for IAM entities"
}

variable "hosted_zone_domain" {
  type        = string
  description = "FQDN for the hosted zone"
}
