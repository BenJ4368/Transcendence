storage "raft" {
  path = "/vault/file"
  node_id = "node1"
}


listener "tcp" {
  address = "vault:8200"
  tls_disable = false
  tls_cert_file = "config/tls/vault.cert"
  tls_key_file = "config/tls/vault.key"
}

api_addr = "https://vault:8200"
cluster_addr = "https://vault:8201"