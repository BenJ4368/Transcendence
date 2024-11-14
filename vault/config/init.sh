#!/bin/sh

# Unseal keys and root token saving path
UNSEAL_KEYS_FILE="/config/unseal-keys.json"
ROOT_TOKEN_FILE="/config/root-token"
DJANGO_TOKEN_FILE="/django/secrets/django-token.txt"
# Secrets (from envv)
SECRETS="POSTGRES_USER POSTGRES_PASSWORD"

# Cheking if a secret already exists in vault
secret_exists() {
    local key="$1" # local variable, wich takes the first argument as value
    vault kv get "kv/$key" > /dev/null 2>&1 # check for the secret in vault redirect output to /dev/null (deleting output)
    return $? # return the ouput code of the command (0 if success, 1 if failed)
}

# Adding secret in vault
add_secret() {
    local key="$1"  # local variable, wich takes the first argument as value
    local value="$2"  # local variable, wich takes the second argument as value

    if secret_exists "$key"; then
        echo "Secret '$key' already exists in Vault. Skipping..."
    else
        echo "Adding secret '$key' to Vault..."
        vault kv put "kv/$key" value="$value"  # add the secret in vault
    fi
}

# Installing jq if not already
if ! command -v jq &> /dev/null; then
    echo "jq not installed. Installing..."
    apk add --no-cache jq
fi

# Checking vault init status
is_init() {
    echo "Checking Vault status..."
    if vault status | grep -q "Initialized.*true"; then
        echo "Vault is initialized."
        return 0
    else
        echo "Vault is not initialized."
        return 1
    fi
}

# Usealing vault using unseal keys
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

# Initializing vault; generates 1 unseal key, 1 root token and saves them in their file.
init_vault() {
    echo "Initializing Vault..."
    init_output=$(vault operator init -format=json -key-shares=1 -key-threshold=1)
    sleep 3
    if [ $? -ne 0 ]; then # command output value -NotEqual to 0
        echo "Failed to initialize Vault."
        exit 1
    fi
    unseal_keys=$(echo "$init_output" | jq -c '.unseal_keys_b64')
    root_token=$(echo "$init_output" | jq -r '.root_token')
    echo "$unseal_keys" > "$UNSEAL_KEYS_FILE"
    echo "$root_token" > "$ROOT_TOKEN_FILE"
    chmod 600 "$UNSEAL_KEYS_FILE" "$ROOT_TOKEN_FILE"
    echo "Vault initialized. Unseal keys and root token have been saved and secured."
    unseal_vault
    vault login $root_token
    vault secrets enable -version=2 kv
    for secret in $SECRETS; do
        value=$(printenv "$secret")
        if [ -n "$value" ]; then # if value is not empty
            add_secret "$secret" "$value"
        else
            echo "Environment variable '$secret' is not set. Skipping..."
        fi
    done
    vault policy write django-policy /config/django-policy.hcl
    vault auth enable approle
    vault write auth/approle/role/django-role \
        secret_id_ttl=1h \
        token_ttl=1h \
        token_max_ttl=4h \
        token_policies=django-policy
    DJANGO_ROLE_ID=$(vault read -field=role_id auth/approle/role/django-role/role-id)
    DJANGO_SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/django-role/secret-id)
    echo "VAULT_ROLE_ID=$DJANGO_ROLE_ID" >> /django/.env
    echo "VAULT_SECRET_ID=$DJANGO_SECRET_ID" >> /django/.env
    echo "VAULT_ROLE_ID=$DJANGO_ROLE_ID"
    echo "VAULT_SECRET_ID=$DJANGO_SECRET_ID"

    # django_token=$(vault token create -policy=django-policy -format=json | jq -r '.auth.client_token')
    # echo "$django_token" > "$DJANGO_TOKEN_FILE"
}

# Main logic; if vault init, unseal; if vault not init, init then unseal;
if is_init; then
    echo "Vault is initialized. Attempting to unseal..."
    if [ -f "$UNSEAL_KEYS_FILE" ] && [ -f "$ROOT_TOKEN_FILE" ]; then
        unseal_vault
        vault auth list
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