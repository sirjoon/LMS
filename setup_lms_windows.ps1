# LMS (Leave Management System) - Windows 10 Installation Script
# PowerShell version for Windows 10/11

param(
    [switch]$UseAltPorts = $false
)

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

Write-Host "🚀 Starting LMS (Leave Management System) Setup for Windows..." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if a port is in use
function Test-Port {
    param($Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker Desktop
if (-not (Test-Command "docker")) {
    Write-Host "❌ Docker Desktop is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Red
    Write-Host "Make sure Docker Desktop is running before executing this script." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
$dockerComposeCmd = ""
if (Test-Command "docker-compose") {
    $dockerComposeCmd = "docker-compose"
} elseif (docker compose version 2>$null) {
    $dockerComposeCmd = "docker compose"
} else {
    Write-Host "❌ Docker Compose is not available." -ForegroundColor Red
    Write-Host "Please install Docker Desktop with Compose support." -ForegroundColor Red
    exit 1
}

# Check Git
if (-not (Test-Command "git")) {
    Write-Host "❌ Git is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Check for port conflicts
Write-Host "🔍 Checking for port conflicts..." -ForegroundColor Yellow
$portConflicts = @()

if (Test-Port 5432) { $portConflicts += "5432 (PostgreSQL)" }
if (Test-Port 6379) { $portConflicts += "6379 (Redis)" }
if (Test-Port 8000) { $portConflicts += "8000 (API)" }
if (Test-Port 5173) { $portConflicts += "5173 (Frontend)" }
if (Test-Port 5050) { $portConflicts += "5050 (pgAdmin)" }

if ($portConflicts.Count -gt 0 -and -not $UseAltPorts) {
    Write-Host "⚠️  Port conflicts detected: $($portConflicts -join ', ')" -ForegroundColor Yellow
    Write-Host "Using alternative ports to avoid conflicts..." -ForegroundColor Yellow
    $UseAltPorts = $true
}

# Step 1: Clone the repository
Write-Host "📥 Cloning LMS repository..." -ForegroundColor Yellow

if (Test-Path "LMS") {
    Write-Host "⚠️  LMS directory already exists. Removing it..." -ForegroundColor Yellow
    Remove-Item -Path "LMS" -Recurse -Force
}

try {
    git clone https://github.com/sirjoon/LMS.git
    Set-Location -Path "LMS"
}
catch {
    Write-Host "❌ Failed to clone repository: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Repository cloned successfully" -ForegroundColor Green

# Step 2: Create directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "api\routers",
    "api\utils",
    "frontend\src\contexts",
    "frontend\src\components",
    "frontend\src\pages\admin",
    "frontend\src\pages\manager",
    "frontend\src\pages\employee",
    "frontend\src\services",
    "frontend\src\test"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host "✅ Directory structure created" -ForegroundColor Green

# Step 3: Organize API files
Write-Host "🔧 Organizing API files..." -ForegroundColor Yellow

$apiFiles = @{
    "api-main.py" = "api\main.py"
    "api-models.py" = "api\models.py"
    "api-database.py" = "api\database.py"
    "api-seed.py" = "api\seed.py"
    "api-requirements.txt" = "api\requirements.txt"
    "api-routers-init.py" = "api\routers\__init__.py"
    "api-admin-router.py" = "api\routers\admin.py"
    "api-manager-router.py" = "api\routers\manager.py"
    "api-employee-router.py" = "api\routers\employee.py"
    "api-shared-router.py" = "api\routers\shared.py"
    "api-auth-router.txt" = "api\routers\auth.py"
    "api-utils-init.py" = "api\utils\__init__.py"
    "api-auth-utils.py" = "api\utils\auth.py"
    "api-logging-config.py" = "api\utils\logging_config.py"
}

foreach ($source in $apiFiles.Keys) {
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $apiFiles[$source] -Force
    }
}

Write-Host "✅ API files organized" -ForegroundColor Green

# Step 4: Organize frontend files
Write-Host "🎨 Organizing frontend files..." -ForegroundColor Yellow

$frontendFiles = @{
    "frontend-package-json.json" = "frontend\package.json"
    "frontend-vite-config.ts" = "frontend\vite.config.ts"
    "frontend-tailwind-config.js" = "frontend\tailwind.config.js"
    "frontend-index-html.html" = "frontend\index.html"
    "frontend-main-tsx.ts" = "frontend\src\main.tsx"
    "frontend-app-tsx.ts" = "frontend\src\App.tsx"
    "frontend-index-css.css" = "frontend\src\index.css"
    "frontend-auth-context.ts" = "frontend\src\contexts\AuthContext.tsx"
    "frontend-api-service.ts" = "frontend\src\services\api.ts"
    "frontend-layout.ts" = "frontend\src\components\Layout.tsx"
    "frontend-loading-spinner.ts" = "frontend\src\components\LoadingSpinner.tsx"
    "frontend-login-page.ts" = "frontend\src\pages\Login.tsx"
    "frontend-test-setup.ts" = "frontend\src\test\setup.ts"
    "frontend-admin-users.ts" = "frontend\src\pages\admin\Users.tsx"
    "frontend-admin-leave-types.ts" = "frontend\src\pages\admin\LeaveTypes.tsx"
    "frontend-admin-holidays.ts" = "frontend\src\pages\admin\Holidays.tsx"
    "frontend-manager-pending.ts" = "frontend\src\pages\manager\PendingRequests.tsx"
    "frontend-manager-history.ts" = "frontend\src\pages\manager\RequestHistory.tsx"
    "frontend-employee-balance.ts" = "frontend\src\pages\employee\LeaveBalance.tsx"
    "frontend-employee-apply.ts" = "frontend\src\pages\employee\ApplyLeave.tsx"
    "frontend-employee-requests.ts" = "frontend\src\pages\employee\RequestHistory.tsx"
}

foreach ($source in $frontendFiles.Keys) {
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $frontendFiles[$source] -Force
    }
}

Write-Host "✅ Frontend files organized" -ForegroundColor Green

# Step 5: Create Docker configuration
Write-Host "🐳 Creating Docker configuration..." -ForegroundColor Yellow

# Determine which docker-compose file to create
if ($UseAltPorts) {
    $composeFile = "docker-compose.yml"
    $frontendPort = "5174"
    $apiPort = "8001"
    $dbPort = "5433"
    $redisPort = "6380"
    $pgadminPort = "5051"
    $apiUrl = "http://localhost:8001"
} else {
    $composeFile = "docker-compose.yml"
    $frontendPort = "5173"
    $apiPort = "8000"
    $dbPort = "5432"
    $redisPort = "6379"
    $pgadminPort = "5050"
    $apiUrl = "http://localhost:8000"
}

@"
version: "3.9"

services:
  api:
    build: ./api
    environment:
      DATABASE_URL: postgresql+psycopg://leave_admin:leave_pass@leave_db:5432/leave_management
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: supersecret_change_in_production
      SEED_DEMO: "true"
      LOG_LEVEL: INFO
      ENVIRONMENT: development
    ports: 
      - "${apiPort}:8000"
    depends_on:
      - leave_db
      - redis
    volumes:
      - ./api:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "${frontendPort}:5173"
    depends_on:
      - api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_BASE_URL: ${apiUrl}
    restart: unless-stopped

  leave_db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: leave_admin
      POSTGRES_PASSWORD: leave_pass
      POSTGRES_DB: leave_management
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    ports:
      - "${dbPort}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U leave_admin -d leave_management"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "${redisPort}:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin123
      PGADMIN_CONFIG_SERVER_MODE: "False"
    ports:
      - "${pgadminPort}:80"
    depends_on:
      - leave_db
    volumes:
      - pgadmin_data:/var/lib/pgadmin

volumes:
  postgres_data:
  redis_data:
  pgadmin_data:
"@ | Out-File -FilePath $composeFile -Encoding UTF8

# Create API Dockerfile
@"
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"@ | Out-File -FilePath "api\Dockerfile" -Encoding UTF8

# Create Frontend Dockerfile
@"
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"@ | Out-File -FilePath "frontend\Dockerfile" -Encoding UTF8

Write-Host "✅ Docker configuration created" -ForegroundColor Green

# Step 6: Fix database.py import issue
Write-Host "🔧 Fixing database import issue..." -ForegroundColor Yellow

@"
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
import os
import structlog

Base = declarative_base()

logger = structlog.get_logger()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://leave_admin:leave_pass@localhost:5432/leave_management")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis client
redis_client = None

async def get_redis():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

async def get_db_async():
    """Async database dependency"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Async database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()
"@ | Out-File -FilePath "api\database.py" -Encoding UTF8

Write-Host "✅ Database import issue fixed" -ForegroundColor Green

# Step 7: Start the application
Write-Host "🚀 Starting LMS application with Docker..." -ForegroundColor Yellow
Write-Host "This may take a few minutes for the first run..." -ForegroundColor Yellow

# Stop any existing containers
try {
    if ($dockerComposeCmd -eq "docker-compose") {
        docker-compose down 2>$null
    } else {
        docker compose down 2>$null
    }
}
catch {
    # Ignore errors if no containers are running
}

# Start the application
try {
    if ($dockerComposeCmd -eq "docker-compose") {
        docker-compose up --build -d
    } else {
        docker compose up --build -d
    }
}
catch {
    Write-Host "❌ Failed to start Docker containers: $_" -ForegroundColor Red
    Write-Host "Make sure Docker Desktop is running and try again." -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
if ($dockerComposeCmd -eq "docker-compose") {
    docker-compose ps
} else {
    docker compose ps
}

# Test the API health
Write-Host "🏥 Testing API health..." -ForegroundColor Yellow
$healthUrl = "http://localhost:$apiPort/health"

for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-Host "✅ API is healthy!" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "⏳ Waiting for API to start... (attempt $i/10)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

# Final status
Write-Host ""
Write-Host "🎉 LMS Setup Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend:      http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "🔧 API:           http://localhost:$apiPort" -ForegroundColor Cyan
Write-Host "📚 API Docs:      http://localhost:$apiPort/docs" -ForegroundColor Cyan
Write-Host "🏥 Health Check:  http://localhost:$apiPort/health" -ForegroundColor Cyan
Write-Host "🗄️  pgAdmin:      http://localhost:$pgadminPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "👥 Demo Users:" -ForegroundColor Yellow
Write-Host "   Admin:    admin / admin123" -ForegroundColor White
Write-Host "   Manager:  manager / manager123" -ForegroundColor White
Write-Host "   Employee: alice / alice123" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the application:" -ForegroundColor Yellow
if ($dockerComposeCmd -eq "docker-compose") {
    Write-Host "   docker-compose down" -ForegroundColor White
} else {
    Write-Host "   docker compose down" -ForegroundColor White
}
Write-Host ""
Write-Host "📋 To view logs:" -ForegroundColor Yellow
if ($dockerComposeCmd -eq "docker-compose") {
    Write-Host "   docker-compose logs -f" -ForegroundColor White
} else {
    Write-Host "   docker compose logs -f" -ForegroundColor White
}
Write-Host ""

# Test API endpoint
Write-Host "🧪 Quick API test:" -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 5
    if ($healthResponse.status -eq "healthy") {
        Write-Host "✅ API is responding correctly!" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  API might still be starting. Please wait a moment and check $healthUrl" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 You can now open http://localhost:$frontendPort in your browser to access the LMS!" -ForegroundColor Green

# Open browser automatically
$openBrowser = Read-Host "Would you like to open the LMS in your default browser? (Y/N)"
if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Process "http://localhost:$frontendPort"
}

