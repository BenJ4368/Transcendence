storage "file" {
    path = "/vault/file"
}

listener "tcp" {
    adress = "0.0.0.0"8200"
    tls_disable = 1
}

disable_mock = true
ui = true