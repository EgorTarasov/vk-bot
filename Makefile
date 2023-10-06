dev:
	python3 main.py --debug 1

deploy:
	docker compose up -d --build

down:
	docker compose down --remove-orphans