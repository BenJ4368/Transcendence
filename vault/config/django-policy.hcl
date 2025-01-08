path "kv/data/*" {
    capabilities = ["create", "read", "list", "update", "delete"]
}
path "kv/data/users/*" {
    capabilities = ["create", "read", "list", "update", "delete"]
}
