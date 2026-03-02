# Multiverse — Docker Deploy

Документация по локальному/серверному запуску проекта **Multiverse** через Docker Compose, если вам не нужен Kubernetes или вы хотите быстро запустить бота с минимальной настройкой.

---

## 📦 Состав сервисов

- **bot** — aiogram-процесс (Python 3.12)
- **redis** — кэш / хранилище FSM
- **mongodb** — база данных
- **mongo-express** — веб-админка для MongoDB *(опционально, по умолчанию доступна на `:8081`)*

---

## 📁 Файлы

- `Dockerfile` — образ бота
- `docker-compose.yml` — оркестрация сервисов
- `.dockerignore` — исключения из контекста сборки
- `.env.example` — шаблон переменных окружения
- `wait_for.py` — ожидание готовности Redis и MongoDB перед стартом бота

---

## ✅ Требования

Перед запуском убедитесь, что у вас установлены:

- Docker
- Docker Compose (плагин `docker compose`)

Проверка:

```bash
docker --version
docker compose version
```

---

## 🚀 Быстрый старт

1. **Скопируйте файлы** (`Dockerfile`, `docker-compose.yml`, `.env.example`, `wait_for.py`) в корень проекта — рядом с `main.py` и `requirements.txt`.

2. **Создайте `.env`** на основе шаблона:

```bash
cp .env.example .env
```

3. **Обязательно укажите `BOT_TOKEN`** в `.env`.

4. **(Рекомендуется)** Убедитесь, что приложение читает строки подключения из переменных окружения:
   - `MONGO_URL`  
     Пример:
     `mongodb://root:example@mongodb:27017/multiverse?authSource=admin`
   - `REDIS_URL`  
     Пример:
     `redis://default:redispass@redis:6379/0`

5. **Запустите проект:**

```bash
docker compose up -d --build
```

---

## 🌐 Доступ к сервисам

- **MongoDB**: `localhost:27017`  
  > Публикацию порта можно убрать в `docker-compose.yml`, если внешний доступ не нужен.

- **Mongo Express**: `http://localhost:8081`

---

## 🛠 Полезные команды

### Логи бота
```bash
docker compose logs -f bot
```

### Перезапуск бота
```bash
docker compose restart bot
```

### Подключиться в контейнер бота
```bash
docker compose exec bot bash
```

### Остановить и удалить контейнеры
```bash
docker compose down
```

### Остановить и удалить контейнеры + volumes (с удалением данных)
```bash
docker compose down -v
```

---

## 🔐 Примечания по безопасности

- Обязательно измените в `.env`:
  - `REDIS_PASSWORD`
  - `MONGO_INITDB_ROOT_PASSWORD`

- Не публикуйте `.env` в репозиторий (добавьте его в `.gitignore`).

- Если `mongo-express` не нужен в production, отключите его в `docker-compose.yml`.

---

## 🧩 Важные замечания по коду

- Если в коде используются хардкоды вроде `localhost:27017` — замените их на переменные окружения:
  - `MONGO_URL`
  - `REDIS_URL`

- Для запуска через **webhook** (вместо polling) добавьте/настройте:
  - `PORT`
  - `WEBHOOK_URL`
  - `WEBAPP_URL`

  И обновите команду запуска (`CMD`) в `Dockerfile` / `docker-compose.yml`.

---

## 📌 Рекомендация для Production

Для production-окружения желательно:

- убрать публикацию MongoDB порта наружу
- ограничить доступ к `mongo-express`
- использовать reverse proxy (Nginx / Traefik)
- хранить секреты в защищённом хранилище (а не только в `.env`)