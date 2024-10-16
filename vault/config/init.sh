#!/bin/sh

VAULT_ADDR="http://0.0.0.0:8200"
UNSEAL_KEYS_FILE="/config/unseal-keys.json"
VAULT_TOKEN_FILE="/config/root-token"

if ! command -v jq &> /dev/null; then
    echo "jq not installed. Installing..."
    apk add --no-cache jq
fi

is_init() {
    vault status &> /dev/null
    return $?
}

init_vault() {
    echo "Initializing Vault..."
    init_output=$(vault operator init -format=json -key-shares=1 -key-threshold=1)

    sleep 5

    unseal_keys=$(echo "$init_output" | jq -c '.unseal_keys_b64')
    root_token=$(echo "$init_output" | jq -r '.root_token')

    echo "$unseal_keys" > "$UNSEAL_KEYS_FILE"
    echo "$root_token" > "$VAULT_TOKEN_FILE"

    echo "Vault initialized. Unseal keys and root token have been saved."
}

unseal_vault() {
    echo "Unsealing Vault..."
    unseal_keys=$(cat "$UNSEAL_KEYS_FILE" | jq -r '.[]')

    for key in $unseal_keys; do
        vault operator unseal "$key"
    done

    echo "Vault unsealed."
}

if is_init; then
    echo "Vault is already initialized. Attempting to unseal..."
    unseal_vault
else
    init_vault
    unseal_vault
fi