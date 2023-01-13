Para desenvolvimento

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up db
```

```bash
docker exec -ti emprega_web sh
```


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