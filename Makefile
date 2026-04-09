target ?= dev

ifeq ($(filter dev prod, $(target)),)
$(error Invalid build target `$(target)`)
endif

DC = docker compose -f docker-compose.yml -f docker-compose-$(target).yml --env-file=.env

DC_EXEC = $(DC) exec -it

build:
	$(DC) up -d --build
	$(if $(filter dev, $(target)), $(DC_EXEC) -it backend uv sync --frozen, )
test:
	$(DC) exec -it backend pytest

down:
	$(DC) down
clean:
	$(DC) down -v --rmi local

enter:
	$(if $(service), , $(error No service provided))
	$(DC_EXEC) $(service) $(or $(command),bash)

enter-backend:
	$(DC_EXEC) backend bash

enter-db:
	$(DC_EXEC) db sh -c 'mysql -u root -p$$MYSQL_ROOT_PASSWORD doc_hub'

enter-redis:
	$(DC_EXEC) redis sh -c 'redis-cli -u redis://$$REDIS_USER:$$REDIS_PASSWORD@localhost:6379'


backup:
	$(DC_EXEC) db sh -c 'mysqldump -u root -p$$MYSQL_ROOT_PASSWORD doc_hub > /var/backup/mysql/db_backup.sql'

	$(DC_EXEC) minio sh -c 'mkdir -p /var/backup/minio/documents /var/backup/minio/images'
	$(DC_EXEC) minio sh -c 'mc alias set doc_hub http://localhost:9000 $$MINIO_ROOT_USER $$MINIO_ROOT_PASSWORD'
	$(DC_EXEC) minio sh -c 'mc mirror --overwrite --remove doc_hub/documents /var/backup/minio/documents/'
	$(DC_EXEC) minio sh -c 'mc mirror --overwrite --remove doc_hub/images /var/backup/minio/images/'

restore:
	$(DC_EXEC) db sh -c 'mysql -u root -p$$MYSQL_ROOT_PASSWORD doc_hub < /var/backup/mysql/db_backup.sql'
	$(DC_EXEC) minio sh -c 'mc alias set doc_hub http://localhost:9000 $$MINIO_ROOT_USER $$MINIO_ROOT_PASSWORD'
	$(DC_EXEC) minio sh -c 'mc mirror --overwrite /var/backup/minio/documents/ doc_hub/documents'
	$(DC_EXEC) minio sh -c 'mc mirror --overwrite /var/backup/minio/images/ doc_hub/images'
