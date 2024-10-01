listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = true
}

storage "raft" {
  path = "/vault/raft"
  node_id = "node1"
}
disable_mlock = true

api_addr = "http://vault:8200"
cluster_addr = "http://vault:8201"
ui = true