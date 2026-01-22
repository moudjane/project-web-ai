.PHONY: run
run:
	uv run fastapi run main.py

.PHONY: db
db:
	docker run --name pgvector-container -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16

# Docker Compose commands
.PHONY: docker-up
docker-up:
	docker-compose up -d

.PHONY: docker-down
docker-down:
	docker-compose down

.PHONY: docker-down-volumes
docker-down-volumes:
	docker-compose down -v

.PHONY: docker-logs
docker-logs:
	docker-compose logs -f

.PHONY: docker-build
docker-build:
	docker-compose build

.PHONY: docker-restart
docker-restart:
	docker-compose restart

.PHONY: docker-ps
docker-ps:
	docker-compose ps
