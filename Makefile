APP_CONTAINER=fastapi-app
APP_IMAGE=fastapi-image
DB_VOLUME=fastapi-db
ALEMBIC = python3 -m alembic -c migrations.ini

build:
	podman build -t $(APP_IMAGE) -f Dockerfile .

run:
	podman run -d --name $(APP_CONTAINER) -v $(PWD):/app -v $(DB_VOLUME):/app/data -p 8000:8000 $(APP_IMAGE)

ssh:
	podman exec -it $(APP_CONTAINER) /bin/bash

stop:
	podman stop $(APP_CONTAINER)
	podman rm $(APP_CONTAINER)

clean: stop
	podman rmi $(APP_IMAGE)
	podman volume rm $(DB_VOLUME)

restart: clean run

init-db:
	$(ALEMBIC) init app/migrations

migration:
	$(ALEMBIC) revision --autogenerate -m "migrations"

upgrade-db:
	$(ALEMBIC) upgrade head

downgrade-db:
	$(ALEMBIC) downgrade -1