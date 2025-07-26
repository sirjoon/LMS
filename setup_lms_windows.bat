@echo off
REM LMS (Leave Management System) - Windows 10 Installation Script
REM Batch file version for Command Prompt

setlocal enabledelayedexpansion

echo 🚀 Starting LMS (Leave Management System) Setup for Windows...
echo ==================================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop is not installed or not in PATH.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo Make sure Docker Desktop is running before executing this script.
    pause
    exit /b 1
)

REM Check Docker Compose
set COMPOSE_CMD=
docker-compose --version >nul 2>&1
if not errorlevel 1 (
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if not errorlevel 1 (
        set COMPOSE_CMD=docker compose
    ) else (
        echo ❌ Docker Compose is not available.
        echo Please install Docker Desktop with Compose support.
        pause
        exit /b 1
    )
)

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed or not in PATH.
    echo Please install Git from: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Check for port conflicts and set ports accordingly
set FRONTEND_PORT=5173
set API_PORT=8000
set DB_PORT=5432
set REDIS_PORT=6379
set PGADMIN_PORT=5050
set API_URL=http://localhost:8000

netstat -an | findstr ":5432" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port conflicts detected. Using alternative ports...
    set FRONTEND_PORT=5174
    set API_PORT=8001
    set DB_PORT=5433
    set REDIS_PORT=6380
    set PGADMIN_PORT=5051
    set API_URL=http://localhost:8001
)

REM Step 1: Clone the repository
echo 📥 Cloning LMS repository...

if exist "LMS" (
    echo ⚠️ LMS directory already exists. Removing it...
    rmdir /s /q "LMS"
)

git clone https://github.com/sirjoon/LMS.git
if errorlevel 1 (
    echo ❌ Failed to clone repository
    pause
    exit /b 1
)

cd LMS
echo ✅ Repository cloned successfully

REM Step 2: Create directory structure
echo 📁 Creating directory structure...

mkdir api\routers 2>nul
mkdir api\utils 2>nul
mkdir frontend\src\contexts 2>nul
mkdir frontend\src\components 2>nul
mkdir frontend\src\pages\admin 2>nul
mkdir frontend\src\pages\manager 2>nul
mkdir frontend\src\pages\employee 2>nul
mkdir frontend\src\services 2>nul
mkdir frontend\src\test 2>nul

echo ✅ Directory structure created

REM Step 3: Organize API files
echo 🔧 Organizing API files...

if exist "api-main.py" copy "api-main.py" "api\main.py" >nul
if exist "api-models.py" copy "api-models.py" "api\models.py" >nul
if exist "api-database.py" copy "api-database.py" "api\database.py" >nul
if exist "api-seed.py" copy "api-seed.py" "api\seed.py" >nul
if exist "api-requirements.txt" copy "api-requirements.txt" "api\requirements.txt" >nul

if exist "api-routers-init.py" copy "api-routers-init.py" "api\routers\__init__.py" >nul
if exist "api-admin-router.py" copy "api-admin-router.py" "api\routers\admin.py" >nul
if exist "api-manager-router.py" copy "api-manager-router.py" "api\routers\manager.py" >nul
if exist "api-employee-router.py" copy "api-employee-router.py" "api\routers\employee.py" >nul
if exist "api-shared-router.py" copy "api-shared-router.py" "api\routers\shared.py" >nul
if exist "api-auth-router.txt" copy "api-auth-router.txt" "api\routers\auth.py" >nul

if exist "api-utils-init.py" copy "api-utils-init.py" "api\utils\__init__.py" >nul
if exist "api-auth-utils.py" copy "api-auth-utils.py" "api\utils\auth.py" >nul
if exist "api-logging-config.py" copy "api-logging-config.py" "api\utils\logging_config.py" >nul

echo ✅ API files organized

REM Step 4: Organize frontend files
echo 🎨 Organizing frontend files...

if exist "frontend-package-json.json" copy "frontend-package-json.json" "frontend\package.json" >nul
if exist "frontend-vite-config.ts" copy "frontend-vite-config.ts" "frontend\vite.config.ts" >nul
if exist "frontend-tailwind-config.js" copy "frontend-tailwind-config.js" "frontend\tailwind.config.js" >nul
if exist "frontend-index-html.html" copy "frontend-index-html.html" "frontend\index.html" >nul
if exist "frontend-main-tsx.ts" copy "frontend-main-tsx.ts" "frontend\src\main.tsx" >nul
if exist "frontend-app-tsx.ts" copy "frontend-app-tsx.ts" "frontend\src\App.tsx" >nul
if exist "frontend-index-css.css" copy "frontend-index-css.css" "frontend\src\index.css" >nul
if exist "frontend-auth-context.ts" copy "frontend-auth-context.ts" "frontend\src\contexts\AuthContext.tsx" >nul
if exist "frontend-api-service.ts" copy "frontend-api-service.ts" "frontend\src\services\api.ts" >nul
if exist "frontend-layout.ts" copy "frontend-layout.ts" "frontend\src\components\Layout.tsx" >nul
if exist "frontend-loading-spinner.ts" copy "frontend-loading-spinner.ts" "frontend\src\components\LoadingSpinner.tsx" >nul
if exist "frontend-login-page.ts" copy "frontend-login-page.ts" "frontend\src\pages\Login.tsx" >nul
if exist "frontend-test-setup.ts" copy "frontend-test-setup.ts" "frontend\src\test\setup.ts" >nul

if exist "frontend-admin-users.ts" copy "frontend-admin-users.ts" "frontend\src\pages\admin\Users.tsx" >nul
if exist "frontend-admin-leave-types.ts" copy "frontend-admin-leave-types.ts" "frontend\src\pages\admin\LeaveTypes.tsx" >nul
if exist "frontend-admin-holidays.ts" copy "frontend-admin-holidays.ts" "frontend\src\pages\admin\Holidays.tsx" >nul
if exist "frontend-manager-pending.ts" copy "frontend-manager-pending.ts" "frontend\src\pages\manager\PendingRequests.tsx" >nul
if exist "frontend-manager-history.ts" copy "frontend-manager-history.ts" "frontend\src\pages\manager\RequestHistory.tsx" >nul
if exist "frontend-employee-balance.ts" copy "frontend-employee-balance.ts" "frontend\src\pages\employee\LeaveBalance.tsx" >nul
if exist "frontend-employee-apply.ts" copy "frontend-employee-apply.ts" "frontend\src\pages\employee\ApplyLeave.tsx" >nul
if exist "frontend-employee-requests.ts" copy "frontend-employee-requests.ts" "frontend\src\pages\employee\RequestHistory.tsx" >nul

echo ✅ Frontend files organized

REM Step 5: Create Docker configuration
echo 🐳 Creating Docker configuration...

(
echo version: "3.9"
echo.
echo services:
echo   api:
echo     build: ./api
echo     environment:
echo       DATABASE_URL: postgresql+psycopg://leave_admin:leave_pass@leave_db:5432/leave_management
echo       REDIS_URL: redis://redis:6379/0
echo       JWT_SECRET: supersecret_change_in_production
echo       SEED_DEMO: "true"
echo       LOG_LEVEL: INFO
echo       ENVIRONMENT: development
echo     ports: 
echo       - "%API_PORT%:8000"
echo     depends_on:
echo       - leave_db
echo       - redis
echo     volumes:
echo       - ./api:/app
echo     restart: unless-stopped
echo     healthcheck:
echo       test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
echo       interval: 30s
echo       timeout: 10s
echo       retries: 3
echo.
echo   frontend:
echo     build: ./frontend
echo     ports:
echo       - "%FRONTEND_PORT%:5173"
echo     depends_on:
echo       - api
echo     volumes:
echo       - ./frontend:/app
echo       - /app/node_modules
echo     environment:
echo       VITE_API_BASE_URL: %API_URL%
echo     restart: unless-stopped
echo.
echo   leave_db:
echo     image: postgres:16
echo     restart: unless-stopped
echo     environment:
echo       POSTGRES_USER: leave_admin
echo       POSTGRES_PASSWORD: leave_pass
echo       POSTGRES_DB: leave_management
echo       POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
echo     ports:
echo       - "%DB_PORT%:5432"
echo     volumes:
echo       - postgres_data:/var/lib/postgresql/data
echo     healthcheck:
echo       test: ["CMD-SHELL", "pg_isready -U leave_admin -d leave_management"]
echo       interval: 10s
echo       timeout: 5s
echo       retries: 5
echo.
echo   redis:
echo     image: redis:7-alpine
echo     restart: unless-stopped
echo     ports:
echo       - "%REDIS_PORT%:6379"
echo     volumes:
echo       - redis_data:/data
echo     healthcheck:
echo       test: ["CMD", "redis-cli", "ping"]
echo       interval: 10s
echo       timeout: 5s
echo       retries: 5
echo.
echo   pgadmin:
echo     image: dpage/pgadmin4
echo     restart: unless-stopped
echo     environment:
echo       PGADMIN_DEFAULT_EMAIL: admin@example.com
echo       PGADMIN_DEFAULT_PASSWORD: admin123
echo       PGADMIN_CONFIG_SERVER_MODE: "False"
echo     ports:
echo       - "%PGADMIN_PORT%:80"
echo     depends_on:
echo       - leave_db
echo     volumes:
echo       - pgadmin_data:/var/lib/pgadmin
echo.
echo volumes:
echo   postgres_data:
echo   redis_data:
echo   pgadmin_data:
) > docker-compose.yml

REM Create API Dockerfile
(
echo FROM python:3.12-slim
echo.
echo # Set working directory
echo WORKDIR /app
echo.
echo # Install system dependencies
echo RUN apt-get update ^&^& apt-get install -y \
echo     curl \
echo     gcc \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo # Copy requirements first for better caching
echo COPY requirements.txt .
echo.
echo # Install Python dependencies
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo # Copy application code
echo COPY . .
echo.
echo # Create non-root user
echo RUN useradd --create-home --shell /bin/bash app \
echo     ^&^& chown -R app:app /app
echo USER app
echo.
echo # Expose port
echo EXPOSE 8000
echo.
echo # Health check
echo HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
echo     CMD curl -f http://localhost:8000/health ^|^| exit 1
echo.
echo # Run the application
echo CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
) > api\Dockerfile

REM Create Frontend Dockerfile
(
echo FROM node:20-alpine
echo.
echo WORKDIR /app
echo.
echo # Copy package files
echo COPY package*.json ./
echo.
echo # Install dependencies
echo RUN npm install
echo.
echo # Copy source code
echo COPY . .
echo.
echo # Expose port
echo EXPOSE 5173
echo.
echo # Start development server
echo CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
) > frontend\Dockerfile

echo ✅ Docker configuration created

REM Step 6: Fix database.py import issue
echo 🔧 Fixing database import issue...

(
echo from sqlalchemy import create_engine, pool
echo from sqlalchemy.orm import sessionmaker
echo from sqlalchemy.ext.declarative import declarative_base
echo import redis.asyncio as redis
echo import os
echo import structlog
echo.
echo Base = declarative_base^(^)
echo.
echo logger = structlog.get_logger^(^)
echo.
echo # Database configuration
echo DATABASE_URL = os.getenv^("DATABASE_URL", "postgresql+psycopg://leave_admin:leave_pass@localhost:5432/leave_management"^)
echo REDIS_URL = os.getenv^("REDIS_URL", "redis://localhost:6379/0"^)
echo.
echo # Create engine with connection pooling
echo engine = create_engine^(
echo     DATABASE_URL,
echo     poolclass=pool.QueuePool,
echo     pool_size=10,
echo     max_overflow=20,
echo     pool_pre_ping=True,
echo     pool_recycle=3600,
echo     echo=os.getenv^("SQL_DEBUG", "false"^).lower^(^) == "true"
echo ^)
echo.
echo # Create session factory
echo SessionLocal = sessionmaker^(autocommit=False, autoflush=False, bind=engine^)
echo.
echo # Redis client
echo redis_client = None
echo.
echo async def get_redis^(^):
echo     """Get Redis client instance"""
echo     global redis_client
echo     if redis_client is None:
echo         redis_client = redis.from_url^(REDIS_URL, decode_responses=True^)
echo     return redis_client
echo.
echo def get_db^(^):
echo     """Database dependency for FastAPI"""
echo     db = SessionLocal^(^)
echo     try:
echo         yield db
echo     except Exception as e:
echo         logger.error^("Database session error", error=str^(e^)^)
echo         db.rollback^(^)
echo         raise
echo     finally:
echo         db.close^(^)
echo.
echo async def get_db_async^(^):
echo     """Async database dependency"""
echo     db = SessionLocal^(^)
echo     try:
echo         yield db
echo     except Exception as e:
echo         logger.error^("Async database session error", error=str^(e^)^)
echo         db.rollback^(^)
echo         raise
echo     finally:
echo         db.close^(^)
) > api\database.py

echo ✅ Database import issue fixed

REM Step 7: Start the application
echo 🚀 Starting LMS application with Docker...
echo This may take a few minutes for the first run...

REM Stop any existing containers
%COMPOSE_CMD% down >nul 2>&1

REM Start the application
%COMPOSE_CMD% up --build -d
if errorlevel 1 (
    echo ❌ Failed to start Docker containers
    echo Make sure Docker Desktop is running and try again.
    pause
    exit /b 1
)

echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
%COMPOSE_CMD% ps

REM Test the API health
echo 🏥 Testing API health...
set HEALTH_URL=http://localhost:%API_PORT%/health

for /L %%i in (1,1,10) do (
    curl -s %HEALTH_URL% >nul 2>&1
    if not errorlevel 1 (
        echo ✅ API is healthy!
        goto :api_ready
    ) else (
        echo ⏳ Waiting for API to start... (attempt %%i/10)
        timeout /t 5 /nobreak >nul
    )
)

:api_ready

REM Final status
echo.
echo 🎉 LMS Setup Complete!
echo ======================
echo.
echo 📱 Frontend:      http://localhost:%FRONTEND_PORT%
echo 🔧 API:           http://localhost:%API_PORT%
echo 📚 API Docs:      http://localhost:%API_PORT%/docs
echo 🏥 Health Check:  http://localhost:%API_PORT%/health
echo 🗄️ pgAdmin:      http://localhost:%PGADMIN_PORT%
echo.
echo 👥 Demo Users:
echo    Admin:    admin / admin123
echo    Manager:  manager / manager123
echo    Employee: alice / alice123
echo.
echo 🛑 To stop the application:
echo    %COMPOSE_CMD% down
echo.
echo 📋 To view logs:
echo    %COMPOSE_CMD% logs -f
echo.

REM Test API endpoint
echo 🧪 Quick API test:
curl -s %HEALTH_URL% | findstr "healthy" >nul 2>&1
if not errorlevel 1 (
    echo ✅ API is responding correctly!
) else (
    echo ⚠️ API might still be starting. Please wait a moment and check %HEALTH_URL%
)

echo.
echo 🎯 You can now open http://localhost:%FRONTEND_PORT% in your browser to access the LMS!

REM Ask to open browser
set /p OPEN_BROWSER="Would you like to open the LMS in your default browser? (Y/N): "
if /i "%OPEN_BROWSER%"=="Y" (
    start http://localhost:%FRONTEND_PORT%
)

echo.
echo Press any key to exit...
pause >nul

