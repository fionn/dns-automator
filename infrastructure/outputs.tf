output "pgp_key_fingerprint" {
  value       = aws_iam_access_key.user.key_fingerprint
  description = "The fingerprint of the PGP key used to encrypt the secret"
}

output "AWS_ACCESS_KEY_ID" {
  value       = aws_iam_access_key.user.id
  description = "The access key ID"
}

output "AWS_SECRET_ACCESS_KEY_encrypted" {
  value       = aws_iam_access_key.user.encrypted_secret
  description = "Encrypted against the provided PGP public key"
}

output "zone_id" {
  value       = aws_route53_zone.zone.zone_id
  description = "The hosted zone ID"
}

output "zone_name" {
  value       = aws_route53_zone.zone.name
  description = "The name of the hosted zone"
}
