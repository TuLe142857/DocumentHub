target ?= dev

ifeq ($(filter dev prod, $(target)),)
$(error Invalid build target `$(target)`)
endif

ifeq ($(target), dev)
DC = docker compose -f docker-compose.yml -f docker-compose-dev.yml --env-file=.env
else
ifeq ($(target), prod)
DC = docker compose -f docker-compose.yml -f docker-compose-prod.yml --env-file=.env
endif
endif

DC_EXEC = $(DC) exec -it

build:
	$(DC) up -d --build

test:
	$(DC) exec -it backend pytest

down:
	$(DC) down
clean:
	$(DC) down -v --rmi local

enter:
	$(if $(service), , $(error No service provided))
	$(if $(command), , $(error No command provided))
	$(DC_EXEC) $(service) $(command)

enter-backend:
	$(DC_EXEC) backend bash

enter-db:
	$(DC_EXEC) db sh -c 'mysql -u root -p$$MYSQL_ROOT_PASSWORD doc_hub'

enter-redis:
	$(DC_EXEC) redis sh -c 'redis-cli -u redis://$$REDIS_USER:$$REDIS_PASSWORD@localhost:6379'
