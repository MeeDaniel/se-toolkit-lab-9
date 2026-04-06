FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    asyncpg \
    pydantic \
    pydantic-settings \
    httpx \
    openai \
    python-dotenv \
    passlib[bcrypt] \
    "bcrypt==4.0.1"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
