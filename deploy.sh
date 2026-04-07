#!/bin/bash
# ============================================
# TourStats - Quick Deploy Script
# ============================================
# Run this on your Ubuntu 24.04 VM to get started.
# Usage: bash deploy.sh
# ============================================

set -e

echo "============================================"
echo "  TourStats - Deployment Setup"
echo "============================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in, then re-run this script."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install it."
    exit 1
fi

echo "✅ Docker: $(docker --version)"
echo "✅ Docker Compose: $(docker compose version)"
echo ""

# Check .env
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env before starting services!"
    echo "   You MUST set at minimum:"
    echo "   - MISTRAL_API_KEY (get from console.mistral.ai)"
    echo "   - POSTGRES_PASSWORD (change from default)"
    echo "   - NANOBOT_ACCESS_KEY (change from default)"
    echo "   - BACKEND_SECRET (change from default)"
    echo "   - CADDY_DOMAIN (set to your domain or VM IP)"
    echo ""
    read -p "Press Enter after you've edited .env, or Ctrl+C to cancel and edit manually..."
    nano .env
    echo ""
fi

# Check MISTRAL_API_KEY
if grep -q "your-mistral-api-key-here" .env; then
    echo "❌ MISTRAL_API_KEY is not set in .env!"
    echo "   Edit .env and set your Mistral API key."
    exit 1
fi

echo "============================================"
echo "  Starting services..."
echo "============================================"
echo ""

docker compose up -d --build

echo ""
echo "============================================"
echo "  Waiting for services to be ready..."
echo "============================================"
echo ""

# Wait for database
echo -n "Waiting for database..."
for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U tourstats &> /dev/null; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "============================================"
echo "  Service Status"
echo "============================================"
echo ""
docker compose ps

echo ""
echo "============================================"
echo "  Access Points"
echo "============================================"
echo ""
echo "  Web App:    http://$(grep CADDY_DOMAIN .env | cut -d= -f2 | tr -d '[:space:]')"
echo "  API Docs:   http://$(grep CADDY_DOMAIN .env | cut -d= -f2 | tr -d '[:space:]')/api/docs"
echo "  Health:     http://$(grep CADDY_DOMAIN .env | cut -d= -f2 | tr -d '[:space:]')/api/health"
echo ""
echo "  View logs:  docker compose logs -f"
echo "  Stop:       docker compose down"
echo ""
echo "============================================"
echo "  Done! 🎉"
echo "============================================"
