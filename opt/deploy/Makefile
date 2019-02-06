update_prod:
	ansible-playbook update_app.yml -i files/production/inventories.yml

restart_prod:
	ansible-playbook restart_docker.yml -i files/production/inventories.yml

deploy_prod: update_prod restart_prod
