# Leave Management System

A comprehensive, production-ready leave management system built with FastAPI, React 18, TypeScript, PostgreSQL, and Redis.

## 🚀 Quick Start

1. **Clone and navigate to the project directory**
   ```bash
   git clone <your-repo-url>
   cd leave-management-system
   ```

2. **Start the entire system**
   ```bash
   docker compose up --build
   ```

3. **Access the applications**
   - **Frontend**: http://localhost:5173
   - **API Documentation**: http://localhost:8000/docs
   - **API Health Check**: http://localhost:8000/health
   - **pgAdmin**: http://localhost:5050 (admin@example.com / admin123)
   - **Redis**: localhost:6379

## 👥 Demo Users

The system comes with pre-seeded demo users:

- **Admin**: username `admin`
- **Manager**: username `manager`
- **Employee**: username `alice`

> **Note**: This is a phase 1 authentication system using username-only login. Select any role in the UI for testing purposes.

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with role-based access control
- Username-only login (phase 1) with hooks for password/MFA expansion
- Three user roles: Admin, Manager, Employee

### 👨‍💼 Admin Features
- **User Management**: Create users, assign roles and managers
- **Leave Type Configuration**: Define leave categories with default quotas
- **Leave Balance Management**: Adjust individual user balances
- **Holiday Management**: Configure corporate holidays and blackout dates

### 👩‍💼 Manager Features
- **Pending Requests**: Review team leave requests
- **Approve/Reject**: Process requests with automatic balance updates
- **Request History**: View all past decisions and request details

### 👨‍💻 Employee Features
- **Leave Balance**: View remaining days across all leave types
- **Apply for Leave**: Submit requests with date validation
- **Holiday Conflict Detection**: Automatic checking against corporate holidays
- **Request History**: Track all submitted requests and their status

## 🏗️ Technical Architecture

### Backend (FastAPI)
- **Python 3.12** + **FastAPI** + **SQLAlchemy 2.x**
- **PostgreSQL 16** with connection pooling
- **Redis** for caching and session management
- **Structured logging** with configurable levels
- **Comprehensive error handling** and monitoring
- **Health checks** and metrics endpoints

### Frontend (React)
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS** for styling
- **React Query** for API state management
- **React Hook Form** + **Zod** for validation
- **React Router** for navigation
- **Toast notifications** for user feedback

### Database Schema
```sql
-- Users with role-based hierarchy
users (id, username, email, role, manager_id)

-- Leave types with default quotas
leave_types (id, name, default_quota)

-- Individual user balances
leave_balances (id, user_id, leave_type_id, remaining_days)

-- Leave requests with approval workflow
leave_requests (id, employee_id, manager_id, leave_type_id, start_date, end_date, status, notes, requested_at, decided_at)

-- Corporate holidays for conflict detection
corporate_holidays (id, date, description)
```

## 🛠️ Development

### Local Development Setup

1. **Start dependencies only**
   ```bash
   docker compose up postgres redis pgadmin
   ```

2. **Run backend locally**
   ```bash
   cd api
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Run frontend locally**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://leave_admin:leave_pass@localhost:5432/leave_management` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing secret | `supersecret_change_in_production` |
| `SEED_DEMO` | Enable demo data seeding | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment mode | `development` |

## 🧪 Testing

### Backend Tests
```bash
cd api
pytest
# Run specific test files
pytest tests/test_auth.py
pytest tests/test_employee.py
```

### Frontend Tests
```bash
cd frontend
npm test
# Run with coverage
npm test -- --coverage
```

### Key Test Scenarios
- ✅ Username-only authentication flow
- ✅ Leave request validation (holidays, balance checks)
- ✅ Manager approval workflow with balance updates
- ✅ Admin balance adjustment functionality
- ✅ Role-based access control enforcement

## 📊 Production Features

### 🔒 Security
- **OWASP-compliant** API security patterns
- **Input validation** and sanitization
- **SQL injection prevention**
- **XSS protection** with proper escaping
- **CORS configuration** for cross-origin requests
- **Rate limiting ready** (configurable)
- **Security headers** middleware

### 📈 Monitoring & Observability
- **Structured logging** with JSON output for production
- **Health check endpoints** for load balancers
- **Request/response logging** with timing metrics
- **Error tracking** with stack traces
- **Database connection monitoring**
- **Redis connectivity checks**

### ⚡ Performance
- **Connection pooling** for PostgreSQL (10 base, 20 overflow)
- **Redis caching** for session management
- **Database query optimization**
- **Async/await patterns** throughout
- **Lazy loading** and pagination ready

### 🐳 Containerization
- **Multi-stage Docker builds** for optimization
- **Non-root user** containers for security
- **Health checks** in Docker Compose
- **Volume persistence** for data
- **Network isolation** between services
- **Graceful shutdown** handling

## 📋 API Endpoints

### Authentication
- `POST /auth/login` - Username-only authentication
- `GET /auth/me` - Get current user details

### Admin Operations
- `POST /admin/users` - Create/update users with roles
- `PATCH /admin/leave-balances/{user_id}` - Adjust user balances
- `POST /admin/leave-types` - Create leave categories
- `POST /admin/holidays` - Add corporate holidays
- `GET /admin/users` - List all users

### Manager Operations
- `GET /manager/requests/pending` - View pending requests
- `POST /manager/requests/{id}/approve` - Approve requests
- `POST /manager/requests/{id}/reject` - Reject requests
- `GET /manager/requests/history` - View decision history

### Employee Operations
- `GET /employee/balance` - View leave balances
- `POST /employee/requests` - Submit leave requests
- `GET /employee/requests` - View request history

### Shared Operations
- `GET /leave-types` - Available leave categories
- `GET /holidays` - Corporate holiday calendar
- `GET /health` - System health status

## 🚦 System Validation

### Business Rules Enforced
- ✅ **Holiday Conflict Detection**: Cannot request leave on corporate holidays
- ✅ **Balance Validation**: Cannot exceed available leave balance
- ✅ **Manager Assignment**: Employees must have assigned managers
- ✅ **Date Validation**: End date must be after start date
- ✅ **Business Days Calculation**: Excludes weekends from leave calculations
- ✅ **Atomic Operations**: Balance updates happen with approvals

### Error Handling
- **422 Unprocessable Entity**: Validation failures (holiday conflicts, insufficient balance)
- **401 Unauthorized**: Invalid or missing authentication
- **403 Forbidden**: Insufficient permissions for role
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: System errors with logging

## 🔄 Workflow Example

1. **Employee** submits leave request
   - System validates dates and balance
   - Checks for holiday conflicts
   - Creates pending request
   - Notifies manager (mock email)

2. **Manager** reviews request
   - Sees employee details and request info
   - Can approve or reject with one click
   - System automatically updates balance on approval

3. **Admin** manages system
   - Creates users and assigns managers
   - Configures leave types and quotas
   - Adjusts individual balances as needed
   - Manages corporate holiday calendar

## 🎯 Production Deployment

The system is production-ready with:

- **Scalable Architecture**: Stateless API design
- **Database Migrations**: SQLAlchemy auto-creation (Alembic ready)
- **Load Balancer Ready**: Health checks and graceful shutdown
- **Monitoring Integration**: Structured logs for Datadog/ELK
- **Security Hardening**: Non-root containers, input validation
- **Performance Optimized**: Connection pooling, caching, async operations

### Recommended Production Setup
```yaml
# docker-compose.prod.yml
version: "3.9"
services:
  api:
    image: your-registry/leave-api:latest
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      JWT_SECRET: ${JWT_SECRET}
    deploy:
      replicas: 3
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    # SSL termination and load balancing
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run full test suite
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using modern web technologies for enterprise-grade leave management.**