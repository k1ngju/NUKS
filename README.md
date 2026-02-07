# Task API (NUKS)

Preprost projekt za seznam opravil
## How to run (Docker Compose)

```bash
docker compose up --build
```

Odpri http://localhost:8000

## How to run (local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Odpri http://localhost:8000

## API documentation

Base URL: `http://localhost:8000`

### 1) List tasks

`GET /api/tasks`

Response:

```json
[
  {
    "id": 1,
    "title": "Kupi mleko",
    "done": false,
    "created_at": "2026-02-06 12:00:00"
  }
]
```

### 2) Create task

`POST /api/tasks`

Request:

```json
{
  "title": "Kupi mleko"
}
```

Response:

```json
{
  "id": 1,
  "title": "Kupi mleko",
  "done": false,
  "created_at": "2026-02-06 12:00:00"
}
```

### 3) Update task

`PUT /api/tasks/{task_id}`

Request (toggle done):

```json
{
  "done": true
}
```

Request (change title):

```json
{
  "title": "Kupi kruh in mleko"
}
```

Response:

```json
{
  "id": 1,
  "title": "Kupi kruh in mleko",
  "done": true,
  "created_at": "2026-02-06 12:00:00"
}
```

### 4) Delete task

`DELETE /api/tasks/{task_id}`

Response:

```json
{
  "status": "deleted"
}
```
