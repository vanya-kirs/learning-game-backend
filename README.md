# Learning Game Backend

A Python backend for an educational role-playing game. Players choose a learning path, complete staged lessons, submit answers, receive progressive hints, and collect rewards. The service records attempts and progress in PostgreSQL.

### Architecture

| Component | Responsibility |
| --- | --- |
| FastAPI router | Validates submissions and exposes game state and learning activities |
| Game and reward services | Apply progression rules, score answers, and grant achievements |
| Content catalog | Resolves lessons, tasks, dialogue, and hints for each learning path |
| SQLAlchemy models | Store attempts, results, progress, and reward records |

### Local inspection

Use Python 3.12 and run the following from the repository root.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest -q
uvicorn main:app
```

Open the interactive API documentation at `/docs`. For authenticated operations, the host application must override `get_web_context` with its identity provider, grant the `student:own` scope, and provision the game tables alongside a UUID-based `users.id` table. Set `DATABASE_URL` to an async PostgreSQL connection URL. The default identity dependency returns HTTP 401.

This public edition contains the game subsystem. The original platform provided account management, guest sessions, and deployment configuration separately.
