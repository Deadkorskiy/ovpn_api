update_prod:
	ansible-playbook update_app.yml -i files/production/inventories.yml

update_telegraf_prod:
	ansible-playbook telegrapf.yml -i files/production/inventories.yml

restart_prod:
	ansible-playbook restart_docker.yml -i files/production/inventories.yml

deploy_prod: update_prod update_telegraf_prod restart_prod
