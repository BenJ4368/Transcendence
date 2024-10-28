#!/bin/sh

# Unseal keys and root token saving path
UNSEAL_KEYS_FILE="/config/unseal-keys.json"
ROOT_TOKEN_FILE="/config/root-token"
DJANGO_TOKEN_FILE="/django/secrets/django-token.txt"
# Secrets (from envv)
SECRETS="POSTGRES_USER POSTGRES_PASSWORD"

# Cheking if secret already exists in vault
secret_exists() {
    local key="$1"
    vault kv get "kv/$key" > /dev/null 2>&1
    return $?
}

# Adding secret in vault
add_secret() {
    local key="$1"
    local value="$2"

    if secret_exists "$key"; then
        echo "Secret '$key' already exists in Vault. Skipping..."
    else
        echo "Adding secret '$key' to Vault..."
        vault kv put "kv/$key" value="$value"
    fi
}

# Installing jq if not already
if ! command -v jq &> /dev/null; then
    echo "jq not installed. Installing..."
    apk add --no-cache jq
fi

# Checking vault init status
is_init() {
    echo "Checking vault status..."
    vault status | grep -q "Initialized.*true"
    return $?
}

# Initializing vault; generates 1 unseal key, 1 root token and saves them in their file.
init_vault() {
    echo "Initializing Vault..."
    init_output=$(vault operator init -format=json -key-shares=1 -key-threshold=1)
    if [ $? -ne 0 ]; then
        echo "Failed to initialize Vault."
        exit 1
    fi
    sleep 3
    unseal_keys=$(echo "$init_output" | jq -c '.unseal_keys_b64')
    root_token=$(echo "$init_output" | jq -r '.root_token')
    echo "$unseal_keys" > "$UNSEAL_KEYS_FILE"
    echo "$root_token" > "$ROOT_TOKEN_FILE"
    echo "Vault initialized. Unseal keys and root token have been saved."
    unseal_vault
    vault login $root_token
    vault secrets enable -version=2 kv
    for secret in $SECRETS; do
        value=$(printenv "$secret")
        if [ -n "$value" ]; then
            add_secret "$secret" "$value"
        else
            echo "Environment variable '$secret' is not set. Skipping..."
        fi
    done
    vault policy write django-policy config/django-policy.hcl
    django_token=$(vault token create -policy=django-policy -format=json | jq -r '.auth.client_token')
    echo "$django_token" > "$DJANGO_TOKEN_FILE"
}

# Usealing vault, cannot be used otherwise; using unseal keys
unseal_vault() {
    echo "Unsealing Vault..."
    unseal_keys=$(cat "$UNSEAL_KEYS_FILE" | jq -r '.[]')
    for key in $unseal_keys; do
        vault operator unseal "$key"
        if [ $? -ne 0 ]; then
            echo "Failed to unseal Vault with key: $key"
            exit 1
        fi
    done
    echo "Vault unsealed."
}

# Main logic; if vault init, unseal; if vault not init, init then unseal;
if is_init; then
    echo "Vault is already initialized. Attempting to unseal..."
    if [ -f "$UNSEAL_KEYS_FILE" ] && [ -f "$ROOT_TOKEN_FILE" ]; then
        unseal_vault
    else
        echo "Error: Unseal keys or root token file not found. Cannot proceed with unsealing."
        exit 1
    fi
else
    init_vault
fi

echo "*******************************************************"
echo "*  Vault operationnal, vault-init will now shut down  *"
echo "*******************************************************"