#!/bin/bash

set -e

trap tf_destroy ERR

function tf_destroy {
    terraform destroy
}

function tf_build {
    terraform validate
    terraform apply
}

function main {
    tf_build
    local output
    output="$(terraform output --json)"
    AWS_ACCESS_KEY_ID=$(echo "$output" | jq -r .AWS_ACCESS_KEY_ID.value)
    echo -e "\e[93mTouch your YubiKey...\e[0m" >&2
    AWS_SECRET_ACCESS_KEY=$(echo "$output" | jq -r .AWS_SECRET_ACCESS_KEY_encrypted.value | base64 --decode | gpg --decrypt 2>/dev/null)
    HOSTED_ZONE_DOMAIN=$(echo "$output" | jq -r .zone_name.value)
    echo "$AWS_ACCESS_KEY_ID"
    echo "$HOSTED_ZONE_DOMAIN"
    heroku config:set AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" HOSTED_ZONE_DOMAIN="$HOSTED_ZONE_DOMAIN"
}

main
