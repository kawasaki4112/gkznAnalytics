# telegram-bot-template

aiogram, postgresql, sqlalchemy

## Docker

Ensure Docker and Docker Compose are installed.

1. Fill in the `.env` and `.env.db` files in the project root:

   # .env

   ```powershell
   Set-Content .env "TOKEN=<your_token>`nAPP_ENV=development`nDATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres"
   ```

   # .env.db

   ```powershell
   Set-Content .env.db "POSTGRES_USER=postgres`nPOSTGRES_PASSWORD=postgres`nPOSTGRES_DB=postgres"
   ```

2. Build and start the services:

```powershell
docker-compose up --build -d
```

3. To stop and remove the containers:

```powershell
docker-compose down
```

The Telegram bot will be available once it connects and starts polling.
