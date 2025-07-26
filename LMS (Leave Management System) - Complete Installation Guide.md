# LMS (Leave Management System) - Complete Installation Guide

## Prerequisites

Before starting, ensure your laptop has the following installed:

### Required Software
1. **Git** - For cloning the repository
2. **Docker Desktop** - For containerized deployment (recommended)
3. **Python 3.11+** - For local development (alternative to Docker)
4. **Node.js 18+** - For frontend development
5. **PostgreSQL 14+** - Database (if not using Docker)
6. **Redis** - Cache service (if not using Docker)

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 2GB free space
- **Network**: Internet connection for downloading dependencies

## Installation Methods

Choose one of the following installation methods:

### Method 1: Docker Installation (Recommended)
### Method 2: Local Installation (Manual Setup)

---

## Method 1: Docker Installation (Recommended)

### Step 1: Install Prerequisites

#### Windows:
1. Download and install **Docker Desktop** from: https://www.docker.com/products/docker-desktop/
2. Download and install **Git** from: https://git-scm.com/downloads
3. Restart your computer after installation

#### macOS:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop and Git
brew install --cask docker
brew install git
```

#### Linux (Ubuntu/Debian):
```bash
# Update package list
sudo apt update

# Install Git
sudo apt install -y git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Logout and login again for group changes to take effect
```

### Step 2: Clone the Repository
```bash
# Clone the repository
git clone https://github.com/sirjoon/LMS.git
cd LMS
```

### Step 3: Organize Project Structure
The repository files need to be organized into proper directories:

```bash
# Create directory structure
mkdir -p api/routers api/utils frontend/src/contexts frontend/src/components
mkdir -p frontend/src/pages/admin frontend/src/pages/manager frontend/src/pages/employee
mkdir -p frontend/src/services frontend/src/test

# Copy API files
cp api-main.py api/main.py
cp api-models.py api/models.py
cp api-database.py api/database.py
cp api-seed.py api/seed.py
cp api-requirements.txt api/requirements.txt

# Copy router files
cp api-routers-init.py api/routers/__init__.py
cp api-admin-router.py api/routers/admin.py
cp api-manager-router.py api/routers/manager.py
cp api-employee-router.py api/routers/employee.py
cp api-shared-router.py api/routers/shared.py
cp api-auth-router.txt api/routers/auth.py

# Copy utils files
cp api-utils-init.py api/utils/__init__.py
cp api-auth-utils.py api/utils/auth.py
cp api-logging-config.py api/utils/logging_config.py

# Copy frontend files
cp frontend-package-json.json frontend/package.json
cp frontend-vite-config.ts frontend/vite.config.ts
cp frontend-tailwind-config.js frontend/tailwind.config.js
cp frontend-index-html.html frontend/index.html
cp frontend-main-tsx.ts frontend/src/main.tsx
cp frontend-app-tsx.ts frontend/src/App.tsx
cp frontend-index-css.css frontend/src/index.css
cp frontend-auth-context.ts frontend/src/contexts/AuthContext.tsx
cp frontend-api-service.ts frontend/src/services/api.ts
cp frontend-layout.ts frontend/src/components/Layout.tsx
cp frontend-loading-spinner.ts frontend/src/components/LoadingSpinner.tsx
cp frontend-login-page.ts frontend/src/pages/Login.tsx

# Copy page files
cp frontend-admin-users.ts frontend/src/pages/admin/Users.tsx
cp frontend-admin-leave-types.ts frontend/src/pages/admin/LeaveTypes.tsx
cp frontend-admin-holidays.ts frontend/src/pages/admin/Holidays.tsx
cp frontend-manager-pending.ts frontend/src/pages/manager/PendingRequests.tsx
cp frontend-manager-history.ts frontend/src/pages/manager/RequestHistory.tsx
cp frontend-employee-balance.ts frontend/src/pages/employee/LeaveBalance.tsx
cp frontend-employee-apply.ts frontend/src/pages/employee/ApplyLeave.tsx
cp frontend-employee-requests.ts frontend/src/pages/employee/RequestHistory.tsx
cp frontend-test-setup.ts frontend/src/test/setup.ts
```

### Step 4: Create Docker Configuration Files

#### Create `docker-compose.yml`:
```bash
cat > docker-compose.yml << 'EOF'
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
      - "8000:8000"
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
      - "5173:5173"
    depends_on:
      - api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_BASE_URL: http://localhost:8000
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
      - "5432:5432"
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
      - "6379:6379"
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
      - "5050:80"
    depends_on:
      - leave_db
    volumes:
      - pgadmin_data:/var/lib/pgadmin

volumes:
  postgres_data:
  redis_data:
  pgadmin_data:
EOF
```

#### Create API Dockerfile:
```bash
cat > api/Dockerfile << 'EOF'
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
EOF
```

#### Create Frontend Dockerfile:
```bash
cat > frontend/Dockerfile << 'EOF'
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
EOF
```


### Step 5: Fix Database Import Issue

The `api/database.py` file needs a small fix. Edit the file and add the missing import:

```bash
# Edit api/database.py
cat > api/database.py << 'EOF'
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
EOF
```

### Step 6: Start the Application

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Step 7: Verify Installation

1. **Check all containers are running:**
```bash
docker-compose ps
```

2. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs  # macOS
# or visit http://localhost:8000/docs in your browser
```

3. **Test the Frontend:**
```bash
# Visit the frontend
open http://localhost:5173  # macOS
# or visit http://localhost:5173 in your browser
```

4. **Access pgAdmin (Database Management):**
```bash
# Visit pgAdmin
open http://localhost:5050  # macOS
# Login: admin@example.com / admin123
```

### Step 8: Test with Demo Users

The system comes with pre-configured demo users:

1. **Admin User:**
   - Username: `admin`
   - Password: `admin123`
   - Role: Administrator

2. **Manager User:**
   - Username: `manager`
   - Password: `manager123`
   - Role: Manager

3. **Employee User:**
   - Username: `alice`
   - Password: `alice123`
   - Role: Employee

### Step 9: Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v
```

---

## Method 2: Local Installation (Manual Setup)

If you prefer not to use Docker or encounter Docker issues:

### Step 1: Install Prerequisites

#### Install Python 3.11+
```bash
# Windows: Download from https://python.org
# macOS:
brew install python@3.11

# Linux:
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

#### Install Node.js 18+
```bash
# Windows: Download from https://nodejs.org
# macOS:
brew install node

# Linux:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Install PostgreSQL
```bash
# Windows: Download from https://postgresql.org
# macOS:
brew install postgresql
brew services start postgresql

# Linux:
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Install Redis
```bash
# Windows: Download from https://redis.io
# macOS:
brew install redis
brew services start redis

# Linux:
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Step 2: Clone and Setup Repository

```bash
# Clone repository
git clone https://github.com/sirjoon/LMS.git
cd LMS

# Organize files (same as Docker method above)
# ... (repeat the file organization commands from Step 3 above)
```

### Step 3: Setup Database

```bash
# Create database and user
sudo -u postgres psql -c "CREATE USER leave_admin WITH PASSWORD 'leave_pass';"
sudo -u postgres psql -c "CREATE DATABASE leave_management OWNER leave_admin;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE leave_management TO leave_admin;"
```

### Step 4: Setup Backend

```bash
# Navigate to API directory
cd api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+psycopg://leave_admin:leave_pass@localhost:5432/leave_management"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET="supersecret_change_in_production"
export SEED_DEMO="true"
export LOG_LEVEL="INFO"
export ENVIRONMENT="development"

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Setup Frontend (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 6: Access the Application

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Troubleshooting

### Common Issues

#### Docker Issues:
```bash
# If Docker containers fail to start
docker-compose down
docker-compose up --build --force-recreate

# Check Docker logs
docker-compose logs api
docker-compose logs frontend
```

#### Port Conflicts:
```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173
netstat -tulpn | grep :5432

# Kill processes using the ports
sudo kill -9 <PID>
```

#### Database Connection Issues:
```bash
# Test PostgreSQL connection
psql -h localhost -U leave_admin -d leave_management

# Restart PostgreSQL
sudo systemctl restart postgresql  # Linux
brew services restart postgresql   # macOS
```

#### Permission Issues (Linux):
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

### Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify all services are running: `docker-compose ps`
3. Test individual components: API health check, database connection
4. Check firewall settings for port access

---

## Next Steps

After successful installation:

1. **Explore the System**: Login with demo users and test workflows
2. **Customize Configuration**: Update environment variables for your needs
3. **Add Real Users**: Use admin interface to add actual users
4. **Configure Email**: Set up SMTP for email notifications
5. **Production Deployment**: Follow production deployment guidelines

## Security Notes

For production use:
- Change default passwords
- Use strong JWT secrets
- Enable HTTPS
- Configure proper firewall rules
- Set up database backups
- Use environment-specific configurations

