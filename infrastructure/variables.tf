variable "region" {
  default = "ap-southeast-1"
}

variable "profile" {
  default = "default"
}

variable "pgp_key" {
  default = "keybase:fionn"
}

variable "path" {
  default = "/application/dns-automator/"
}

variable "hosted_zone_domain" {
  type        = string
  description = "FQDN for the hosted zone"
}
