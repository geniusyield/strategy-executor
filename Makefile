all : start stop
.PHONY : all

start:
	docker compose up -d --build strategy_a
	docker compose logs -f

start-a:
	docker compose up -d --build strategy_a
	docker compose logs -f

start-b:
	docker compose up -d --build strategy_b
	docker compose logs -f

stop:
	docker compose down
