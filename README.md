# SaturChat Backend

This is the Django-based backend API for **SaturChat**, a collaborative group chat platform with real-time messaging, AI assistants, and profile management.

---

## Features

- **Real-time Chat** with Django Channels & WebSockets
- **AI Assistants** powered by OpenAI, Anthropic (Claude), and Gemini
- **JWT Authentication** with access/refresh tokens
- **User Profiles** with avatar uploads and API key management
- **Group Chats** with participant management and permissions
- **Async Task Queue** using Celery and Redis
- **PostgreSQL** for relational data storage
- **Fully Containerized** via Docker

---

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/saturchat-backend.git
cd saturchat-backend
```

### 2. Create Environment File

Copy the template and edit values as needed:

```bash
cp .env.production .env
```

### 3. Build & Run with Docker Compose

```bash
docker-compose up --build
```

This will start:
- Django API via Daphne (ASGI)
- Celery worker & beat
- PostgreSQL
- Redis

---

## Environment Variables

Here are the required environment variables:

```env
# Django settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=saturchat
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Other
CLEAN_OLD_MESSAGES=True
SALT_KEY=your-salt-key
```

---

## AI Bots

Add any of the following bot usernames as participants:

- `@chatgpt` → uses OpenAI
- `@claude` → uses Anthropic
- `@gemini` → uses Gemini

The admin of the group must provide the corresponding API key.

---

## Deployment

The backend is containerized and designed to run behind an NGINX reverse proxy.

It is also CI/CD-ready with support for GitHub Container Registry and Docker Compose in production.

---

## License

This project is licensed under the MIT License.

