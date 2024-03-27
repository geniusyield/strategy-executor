all : start stop
.PHONY : all

start:
	docker compose up --build

stop:
	docker compose down
