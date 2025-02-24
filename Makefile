APP_CONTAINER=fastapi-app
APP_IMAGE=fastapi-image
DB_VOLUME=fastapi-db
ALEMBIC = python3 -m alembic -c generator.ini

build:
	podman build -t $(APP_IMAGE) -f Dockerfile .

run: build
	podman run -d --name $(APP_CONTAINER) -v $(PWD):/app:Z -v $(DB_VOLUME):/app/data -p 8000:8000 $(APP_IMAGE)

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
	$(ALEMBIC) init app/generator

migration:
	$(ALEMBIC) revision --autogenerate -m "generator"

upgrade-db:
	$(ALEMBIC) upgrade head

downgrade-db:
	$(ALEMBIC) downgrade -1