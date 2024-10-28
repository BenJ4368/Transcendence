storage "raft" {
  path = "/vault/file"
  node_id = "node1"
}


listener "tcp" {
  address = "vault:8200"
  tls_disable = true
}

api_addr = "http://vault:8200"
cluster_addr = "http://vault:8201"