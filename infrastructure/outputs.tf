output "pgp_key_fingerprint" {
  value = "${aws_iam_access_key.user.key_fingerprint}"
}

output "AWS_ACCESS_KEY_ID" {
  value = "${aws_iam_access_key.user.id}"
}

output "AWS_SECRET_ACCESS_KEY_encrypted" {
  value       = "${aws_iam_access_key.user.encrypted_secret}"
  description = "Encrypted against the provided PGP public key"
}

output "zone_id" {
  value = "${aws_route53_zone.zone.zone_id}"
}

output "zone_name" {
  value = "${aws_route53_zone.zone.name}"
}
