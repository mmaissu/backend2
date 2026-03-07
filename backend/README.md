# Scientific Data Harvester — Backend

RESTful API для сбора и анализа метаданных научных публикаций.

## Запуск

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Тесты

```bash
uv run pytest -v --cov=app
```
