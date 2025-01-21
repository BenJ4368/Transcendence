RED=\033[31m
YEL=\033[33m
CYA=\033[36m
STOP=\033[0m

all: #Builds, then starts all containers. Entrypoint of ft_transcendence
	@echo "$(CYA)=== Composing Transcendence...$(STOP)"
	@sudo openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
        -out vault/config/tls/vault.cert \
        -keyout vault/config/tls/vault.key \
        -subj "/C=FR/ST=MULHOUSE/L=MULHOUSE/O=42 School/OU=transcendence/CN=transcendence/" \
		-addext "subjectAltName = DNS:vault"
	@sudo cp vault/config/tls/vault.cert web/django/tls/vault.cert && sudo cp vault/config/tls/vault.key web/django/tls/vault.key
	@sudo docker-compose up --build -d redis postgresql vault
	@echo "$(YEL)=== Waiting for Redis, PostgreSQL and Vault (10s)$(STOP)"
	@sleep 10
	@sudo docker-compose up --build -d vault-init
	@echo "$(YEL)=== Initializing Vault (30s)$(STOP)"
	@sleep 30
	@sudo docker-compose up --build -d web nginx
	@sudo docker-compose logs -f web

reload: #stops and rebuilds the web and nginx containers
	@echo "$(CYA)=== Reloading web and nginx...$(STOP)"
	@sudo docker-compose stop web nginx
	@sudo docker-compose up --build -d web nginx
	@sudo docker-compose logs -f web

clean: #Stops and remove all containers volumes and networks
	@echo "$(CYA)=== Stopping and cleaning containers, volumes and networks...$(STOP)"
	@sudo docker stop $$(sudo docker ps -qa);\
	 sudo docker rm $$(sudo docker ps -qa);\
	 sudo docker volume rm $$(sudo docker volume ls -q);\
	 sudo docker network rm $$(sudo docker network ls -q)

iclean: #Removes all images
	@echo "$(RED)!!!=== Do you really want to remove all images ?$(STOP)"
	@read -p "Confirm (y/n) : " confirm && [ "$$confirm" = "y" ] || (echo "$(YEL)Aborted.$(STOP)" && exit 1)
	@echo "$(CYA)=== Cleaning images...$(STOP)"
	@sudo docker rmi $$(sudo docker images -qa);


fclean: #Removes all files contained in the volumes
	@echo "$(RED)!!!=== Do you really want to remove all data ?\n$(YEL) /!\ This will delete all persisted data (keys, users, scores...) /!\ $(STOP)"
	@read -p "Confirm (y/n) : " confirm && [ "$$confirm" = "y" ] || (echo "$(YEL)Aborted.$(STOP)" && exit 1)
	@echo "$(CYA)=== Cleaning data...$(STOP)"
	@sudo rm -rf postgresql/data vault/volume/* vault/config/root-token vault/config/unseal-keys.json vault/config/tls/* web/django/tls/*
	@sed -i '/^VAULT_ROLE_ID=/d' web/.env
	@sed -i '/^VAULT_SECRET_ID=/d' web/.env
	@make clean

list: #Lists all containers, images, volumes and networks. Running or not, used or not.
	@echo "\n$(CYA)======== CONTAINERS ========$(STOP)"
	@sudo docker ps -a
	@echo "\n$(CYA)======== IMAGES ============$(STOP)"
	@sudo docker images -a
	@echo "\n$(CYA)======== VOLUMES ===========$(STOP)"
	@sudo docker volume ls
	@echo "\n$(CYA)======== NETWORKS ==========$(STOP)"
	@sudo docker network ls

.PHONY: all start stop clean iclean fclean lsit
