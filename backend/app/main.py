from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routes import excursions, chat, statistics, users
from app.services import ai_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables and handle schema migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Migration: Rename telegram_alias to login if needed
        try:
            await conn.execute("""
                DO $$
                BEGIN
                    -- Check if old column exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'telegram_alias'
                    ) THEN
                        -- Rename column
                        ALTER TABLE users RENAME COLUMN telegram_alias TO login;
                        
                        -- Remove requires_password if exists
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'requires_password'
                        ) THEN
                            ALTER TABLE users DROP COLUMN requires_password;
                        END IF;
                        
                        -- Make password_hash NOT NULL (set default for any NULL)
                        UPDATE users SET password_hash = '' WHERE password_hash IS NULL;
                        ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;
                    END IF;
                    
                    -- Add password_hash column if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'password_hash'
                    ) THEN
                        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';
                    END IF;
                    
                    -- Add login column if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'login'
                    ) THEN
                        ALTER TABLE users ADD COLUMN login VARCHAR(100) UNIQUE NOT NULL DEFAULT '';
                    END IF;

                    -- Add auth_token column if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name = 'auth_token'
                    ) THEN
                        ALTER TABLE users ADD COLUMN auth_token VARCHAR(64) UNIQUE DEFAULT NULL;
                    END IF;
                END $$;
            """)
        except Exception as e:
            print(f"Migration note: {e}")
    yield
    # Shutdown: Clean up resources if needed
    await engine.dispose()


app = FastAPI(
    title="Hackathon API",
    description="AI-powered statistics app for Innopolis tour guides",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # Custom docs path
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(excursions.router, prefix="/api/excursions", tags=["excursions"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "message": "Hackathon API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
