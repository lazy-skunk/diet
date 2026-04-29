## Docker

```bash
docker compose build --no-cache
docker compose up -d
docker compose stop
docker compose down --rmi all
```

## Flask

```bash
flask run
```

## Git

```bash
git branch --merged main | grep -vE '^\*| main$' | xargs -r git branch -d
```
