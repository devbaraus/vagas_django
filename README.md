Para desenvolvimento

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Reset do banco de dados
```bash
docker volume rm emprega_base
docker volume create emprega_base
docker rm -rf emprega_base
```

Para produção
```bash 
docker volume create --name=emprega_base
docker compose -f docker-compose.yml up -d
```