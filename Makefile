all : start stop
.PHONY : all

start:
	docker compose up --build strategy_a

start-a:
	docker compose up --build strategy_a

start-b:
	docker compose up --build strategy_b

stop:
	docker compose down
