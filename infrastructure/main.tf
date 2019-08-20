resource "aws_route53_zone" "zone" {
  name          = var.hosted_zone_domain
  force_destroy = "true"
}

resource "aws_iam_user" "user" {
  name = "dns-automator-prod"
  path = var.path
}

resource "aws_iam_group" "group" {
  name = "dns-automator"
  path = var.path
}

resource "aws_iam_user_group_membership" "membership" {
  user   = aws_iam_user.user.name
  groups = [aws_iam_group.group.name]
}

resource "aws_iam_access_key" "user" {
  user    = aws_iam_user.user.name
  pgp_key = var.pgp_key
}

data "aws_iam_policy_document" "dns_automator" {
  statement {
    actions = [
      "route53:ChangeResourceRecordSets",
      "route53:ListResourceRecordSets"
    ]
    resources = ["arn:aws:route53:::hostedzone/${aws_route53_zone.zone.zone_id}"]
  }
  statement {
    actions   = ["route53:ListHostedZones"]
    resources = ["*"]
  }
}

resource "aws_iam_group_policy" "policy" {
  name   = "route53-dns-automator"
  group  = aws_iam_group.group.id
  policy = data.aws_iam_policy_document.dns_automator.json
}
