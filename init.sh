docker swarm init
docker build -t botflix:latest .
docker stack deploy --compose-file docker-compose.yml botflix
