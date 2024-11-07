all: #Builds, then starts all containers. Entrypoint of ft_transcendence
	@echo "Composing Transcendence..."
	@sudo docker-compose up --build

start: #Starts stopped containers, without re-building them
	@echo "Starting containers..."
	@sudo docker-compose up

stop: #Stops containers, does not remove them
	@echo "Stopping containers..."
	@sudo docker-compose stop

clean: #Stops and remove all containers, images, volumes and networks
	@echo "Cleaning..."
	@sudo docker stop $$(sudo docker ps -qa);\
	 sudo docker rm $$(sudo docker ps -qa);\
	 sudo docker volume rm $$(sudo docker volume ls -q);\
	 sudo docker network rm $$(sudo docker network ls -q)

iclean: #Removes all images
	@echo "Cleaning..."
	@sudo docker rmi $$(sudo docker images -qa);

fclean:
	@sudo rm -rf vault/volume/* vault/config/root-token vault/config/unseal-keys.json django/secrets/* 

list: #Lists all containers, images, volumes and networks. Running or not, used or not.
	@echo "INCEPTION LISTING:"
	@echo "\n======== CONTAINERS ========"
	@sudo docker ps -a
	@echo "\n======== IMAGES ========"
	@sudo docker images -a
	@echo "\n======== VOLUMES ========"
	@sudo docker volume ls
	@echo "\n======== NETWORKS ========"
	@sudo docker network ls

.PHONY: all down clean list
