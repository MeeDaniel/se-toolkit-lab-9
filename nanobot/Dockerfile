FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir \
    websockets \
    httpx \
    openai \
    pydantic \
    pydantic-settings \
    python-dotenv \
    uvicorn \
    fastapi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the nanobot agent
CMD ["python", "-m", "app.main"]
