all:
	@echo "Composing Transcendence..."
	@sudo docker-compose up --build

down:
	@echo "Shutting down docker-composed containers..."
	@sudo docker-compose down

clean:
	@echo "Stopping and removing containers, images, volumes and networks..."
	@sudo docker stop $$(sudo docker ps -qa);\
	 sudo docker rm $$(sudo docker ps -qa);\
	 sudo docker rmi $$(sudo docker images -qa);\
	 sudo docker volume rm $$(sudo docker volume ls -q);\
	 sudo docker network rm $$(sudo docker network ls -q)

list:
	@echo "INCEPTION LISTING:"
	@echo "======== CONTAINERS"
	@sudo docker ps -a
	@echo "======== IMAGES"
	@sudo docker images -a
	@echo "======== VOLUMES"
	@sudo docker volume ls
	@echo "======== NETWORKS"
	@sudo docker network ls

.PHONY: all down clean list
