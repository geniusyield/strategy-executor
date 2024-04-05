all : start stop
.PHONY : all

DEFAULT_STRATEGY := strategy_a

start:
	docker compose up -d --build $(DEFAULT_STRATEGY)
	docker compose logs -f strategy_a

start-a:
	docker compose up -d --build strategy_a
	docker compose logs -f

start-b:
	docker compose up -d --build strategy_b
	docker compose logs -f

stop:
	docker compose down

get-settings:
	curl -H "api-key: ${SERVER_API_KEY}" localhost:8082/v0/settings/ && echo

get-assets:
	curl -H "api-key: $(SERVER_API_KEY)" localhost:8082/v0/assets/c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53 && echo

get-fees:
	curl -H "api-key: $(SERVER_API_KEY)" localhost:8082/v0/trading-fees && echo

get-markets:
	curl -H "api-key: $(SERVER_API_KEY)" localhost:8082/v0/markets && echo

get-order-book:
	curl -H "api-key: $(SERVER_API_KEY)" localhost:8082/v0/order-book/lovelace_c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53 && echo

place-order:
	curl -X POST localhost:8082/v0/orders -H "Content-Type: application/json" -H "api-key: ${SERVER_API_KEY}" -d '{"offer_amount": "1", "offer_token": "lovelace", "price_amount": "1", "price_token": "66a524d7f34d954a3ad30b4e2d08023c950dfcd53bbe3c2314995da6.744d454c44", "address":"addr_test1qz9zh342r6ynfhk974tmjxxxznrmmh0tre09tdh6gc3r6r2rq3uxt0yu4c0mg2ck6h8f0h3ykh7n4w68f7dr3mfch58q6rhtxg"}'

cancel-order:
	curl -X DELETE "localhost:8082/v0/orders" -H "Content-Type: application/json" -H "api-key: ${SERVER_API_KEY}" -d '{"address": "addr_test1qz9zh342r6ynfhk974tmjxxxznrmmh0tre09tdh6gc3r6r2rq3uxt0yu4c0mg2ck6h8f0h3ykh7n4w68f7dr3mfch58q6rhtxg","order_references": [ "50edb8d98a503c83e04b4d3a828150797f6fc2c6e096f40e67f803b13032bb85#0"] }'

get-historical-prices:
	curl -X GET "localhost:8082/v0/historical-prices/maestro/lovelace_c6e65ba7878b2f8ea0ad39287d3e2fd256dc5c4160fc19bdf4c4d87e.7447454e53/genius-yield?resolution=1h&from=2024-01-01&to=2024-01-02" -H "api-key: ${SERVER_API_KEY}"