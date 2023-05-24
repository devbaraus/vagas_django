Para desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up
```

ou

```bash
docker compose -f docker-compose.yml up
```

e

```bash
docker compose -f docker-compose.dev.yml  up db
```

ou

```bash
docker compose -f docker-compose.yml up db
```

Entre no container pelo comando:
```bash
docker exec -ti emprega_web sh ##ou /bin/bash##
```
Rode o seguinte comando no sh ou /bin/bash:
```bash
  python manage.py createsuperuser
```
>* Obs: Cadastre o superuser conforme indicado, lembrando de ter data de nascimento maior que 14 anos e no formato YYYY-MM-DD, senha com mais de 8 caracteres, sendo numéricos, letra maiúscula, minúscula e caractere especial.

Reset do banco de dados
```bash
docker volume rm emprega_base
docker volume create emprega_base
sudo rm -rf emprega_base
```

Para produção
```bash 
docker volume create --name=emprega_base
docker compose -f docker-compose.yml up -d
```