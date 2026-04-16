# Scientific Data Harvester

Сервис сбора и анализа метаданных научных публикаций.

## Архитектура

- **Backend**: FastAPI, async SQLAlchemy (PostgreSQL), JWT (User/Admin), Pydantic, bcrypt
- **Frontend**: React + Vite + TypeScript
- **БД**: PostgreSQL 16
- **Безопасность**: хеширование паролей, заголовки XSS, параметризованные запросы (защита от SQLi)

## Запуск через Docker

1. Откройте терминал в папке проекта:
   ```powershell
   cd "C:\Users\Maira Suleimen\scientific-data-harvester"
   ```
2. Запустите контейнеры (первый раз сборка займёт несколько минут):
   ```powershell
   docker compose up --build
   ```
   Окно не закрывайте — в нём будут логи. Дождитесь строк:
   - `Application startup complete` (backend)
   - контейнеры `db`, `backend`, `frontend` в статусе Up.

3. Откройте в браузере:
   - **Фронт (приложение):** http://localhost:3000  
   - **API:** http://localhost:8000/api  
   - **Документация API:** http://localhost:8000/api/docs  
- **Метрики backend:** http://localhost:8000/metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (по умолчанию `admin/admin`)

Если видите «can't reach this page» / «refused to connect»:
- Убедитесь, что Docker Desktop запущен.
- Проверьте контейнеры: в **другом** терминале выполните `docker compose ps` — все три сервиса должны быть **Up**. Если какой-то Exited — смотрите логи: `docker compose logs backend` или `docker compose logs frontend`.
- Можно запускать в фоне: `docker compose up --build -d`, затем открыть ссылки через 15–20 секунд.  

### Production-профиль

Создайте `.env` на основе `.env.example` и поднимайте стек:

```powershell
copy .env.example .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Grafana автоматически поднимается с преднастроенным Prometheus datasource и дашбордом `Scientific Data Harvester`.

## Роль администратора (Admin)

**Вариант 1 — при регистрации:** задайте переменную окружения `INITIAL_ADMIN_EMAIL` (ваш email). При регистрации пользователя с этим email ему присвоится роль Admin.

```powershell
$env:INITIAL_ADMIN_EMAIL = "mairasuleimen@icloud.com"
docker compose up --build -d
```

Затем зарегистрируйте **новый** аккаунт с этим email — он будет Admin. (Если такой email уже есть, используйте вариант 2.)

**Вариант 2 — выдать Admin уже зарегистрированному пользователю:** выполните SQL в БД:

```powershell
docker compose exec db psql -U harvester -d harvester -c "UPDATE users SET role = 'ADMIN' WHERE email = 'mairasuleimen@icloud.com';"
```
(Если будет ошибка про enum, попробуйте `'admin'` вместо `'ADMIN'`.)

После этого войдите под этим email — в токене будет роль `admin`.

## Локальная разработка

### Backend

```bash
cd backend
pip install -e ".[dev]"
# PostgreSQL должен быть запущен (или docker compose up db)
export DATABASE_URL=postgresql+asyncpg://harvester:harvester@localhost:5432/harvester
uvicorn app.main:app --reload --port 8000
pytest -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Прокси на API: запросы к `/api` идут на `http://localhost:8000`.

## Тестирование

### Unit + Integration (pytest)

Тесты используют **реальный Postgres** (модели содержат `UUID/JSONB`), поэтому для безопасного запуска нужен отдельный тестовый URL.

Пример (если Postgres из `docker-compose.yml` запущен и доступен на `localhost:5433`):

```bash
cd backend

# 1) (один раз) создайте отдельную тестовую БД
docker compose exec db psql -U harvester -d harvester -c "CREATE DATABASE harvester_test;" || true

# 2) запустите тесты
export TEST_DATABASE_URL=postgresql+asyncpg://harvester:harvester@localhost:5433/harvester_test
uv run pytest -v --cov=app --cov-report=term-missing
```

Структура тестов:
- `backend/tests/test_unit_*.py`
- `backend/tests/test_integration_*.py`

### Load test (k6)

```bash
k6 run load-tests/k6_script.js
```

Можно переопределить базовый URL:

```bash
BASE_URL=http://localhost:8000 k6 run load-tests/k6_script.js
```

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход (JWT) |
| GET | /api/auth/me | Текущий пользователь (Bearer) |
| GET | /api/articles | Список статей (поиск, фильтр source, пагинация, сортировка) |
| GET | /api/articles/{id} | Одна статья |
| POST | /api/articles | Создать статью (auth) |
| PATCH | /api/articles/{id} | Обновить (автор или Admin) |
| DELETE | /api/articles/{id} | Удалить (автор или Admin) |

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`): на push/PR в `main`/`develop` — тесты backend (pytest + Postgres), сборка frontend.

## Структура проекта

```
scientific-data-harvester/
├── backend/           # FastAPI, Clean Architecture
│   ├── app/
│   │   ├── api/       # Роуты auth, articles
│   │   ├── core/      # security, deps (JWT, get_current_user)
│   │   ├── domain/    # enums (UserRole)
│   │   ├── infrastructure/  # database, models, metrics
│   │   ├── middleware/      # Security headers
│   │   └── schemas/   # Pydantic
│   └── tests/
├── frontend/          # React + Vite
├── docker-compose.yml
└── .github/workflows/ci.yml
```
