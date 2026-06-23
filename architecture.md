# Architecture
flowchart TB

    User[User]

    subgraph DockerCompose["Docker Compose Environment"]
    
        API[FastAPI API Service]

        Redis[(Redis Queue)]

        Worker[Celery Worker]

        Postgres[(PostgreSQL)]

        LLM[Gemini/OpenAI]

    end

    User -->|Upload CSV| API

    API -->|Create Job| Postgres

    API -->|Enqueue Job| Redis

    Redis -->|Consume Job| Worker

    Worker -->|Read/Write Data| Postgres

    Worker -->|Category Classification| LLM

    Worker -->|Narrative Summary| LLM

    User -->|GET Status| API

    User -->|GET Results| API

    API -->|Fetch Results| Postgres