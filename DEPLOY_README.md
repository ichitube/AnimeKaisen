# Multiverse — Docker Deploy

## Состав
- **bot** — aiogram-процесс (Python 3.12).
- **redis** — кеш/хранилище FSM.
- **mongodb** — база данных.
- **mongo-express** — веб‑админка для Mongo (опционально, по умолчанию включена на :8081).

## Файлы
- `Dockerfile` — образ бота.
- `docker-compose.yml` — оркестрация сервисов.
- `.dockerignore` — исключения из контекста сборки.
- `.env.example` — шаблон переменных окружения.
- `wait_for.py` — ожидание готовности Redis и Mongo перед стартом бота.

## Быстрый старт
1) Скопируйте эти файлы в корень проекта рядом с `main.py` и `requirements.txt`.
2) Создайте `.env` на основе `.env.example` и обязательно укажите `BOT_TOKEN`.
3) (Не обязательно) Убедитесь, что в коде вы читаете строки подключения из env:
   - `MONGO_URL` (например: `mongodb://root:example@mongodb:27017/multiverse?authSource=admin`)
   - `REDIS_URL` (например: `redis://default:redispass@redis:6379/0`)
4) Запуск:
```bash
docker compose up -d --build
```

Mongo будет доступен локально на `27017` (можно убрать публикацию порта в compose). Mongo‑Express откроется на `http://localhost:8081`.

## Полезные команды
```bash
# Логи бота
docker compose logs -f bot

# Перезапуск
docker compose restart bot

# Подключиться в контейнер бота
docker compose exec bot bash

# Остановить/удалить
docker compose down
docker compose down -v   # с удалением данных
```

## Примечания
- **Безопасность**: измените `REDIS_PASSWORD` и `MONGO_INITDB_ROOT_PASSWORD` в `.env`.
- Если ваш код сейчас использует хардкоды вроде `localhost:27017` — замените на переменные окружения `MONGO_URL`/`REDIS_URL`.
- Если вы используете webhooks вместо polling — добавьте `PORT`, `WEBHOOK_URL`, `WEBAPP_URL` и соответствующий запуск в `CMD`.
