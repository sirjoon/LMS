# 🚀 **Complete Step-by-Step Execution Guide**

## **Phase 1: Setup Your Environment**

### **Prerequisites Check**
```bash
# Verify you have these installed:
docker --version          # Should show Docker version
docker-compose --version  # Should show Compose version
git --version             # Should show Git version
```

**If missing, install:**
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- **Git**: https://git-scm.com/downloads

---

## **Phase 2: Create Project Structure**

### **Step 1: Create Root Directory**
```bash
# Create main project folder
mkdir leave-management-system
cd leave-management-system

# Initialize git
git init
```

### **Step 2: Create Directory Structure**
```bash
# Create all required directories
mkdir -p api/routers
mkdir -p api/utils
mkdir -p frontend/src/contexts
mkdir -p frontend/src/components
mkdir -p frontend/src/pages/admin
mkdir -p frontend/src/pages/manager
mkdir -p frontend/src/pages/employee
mkdir -p frontend/src/services
mkdir -p frontend/src/test

# Verify structure
tree . # or ls -la on Windows
```

---

## **Phase 3: Create All Files**

### **Step 3A: Root Files**

**Create `docker-compose.yml`:**
```bash
# Copy the entire docker-compose.yml content from my artifact above
# Save as: docker-compose.yml
```

**Create `README.md`:**
```bash
# Copy the entire README.md content from my artifact above
# Save as: README.md
```

### **Step 3B: Backend Files (API)**

**Create each file in the `api/` directory:**

1. **`api/Dockerfile`** - Copy from artifact
2. **`api/requirements.txt`** - Copy from artifact
3. **`api/main.py`** - Copy from artifact
4. **`api/models.py`** - Copy from artifact
5. **`api/database.py`** - Copy from artifact
6. **`api/seed.py`** - Copy from artifact

**Create router files in `api/routers/`:**

7. **`api/routers/__init__.py`** - Copy from artifact
8. **`api/routers/auth.py`** - Copy from artifact
9. **`api/routers/admin.py`** - Copy from artifact
10. **`api/routers/manager.py`** - Copy from artifact
11. **`api/routers/employee.py`** - Copy from artifact
12. **`api/routers/shared.py`** - Copy from artifact

**Create utility files in `api/utils/`:**

13. **`api/utils/__init__.py`** - Copy from artifact
14. **`api/utils/auth.py`** - Copy from artifact
15. **`api/utils/logging_config.py`** - Copy from artifact

### **Step 3C: Frontend Files**

**Create root frontend files:**

16. **`frontend/Dockerfile`** - Copy from artifact
17. **`frontend/package.json`** - Copy from artifact
18. **`frontend/vite.config.ts`** - Copy from artifact
19. **`frontend/tailwind.config.js`** - Copy from artifact
20. **`frontend/index.html`** - Copy from artifact

**Create core React files in `frontend/src/`:**

21. **`frontend/src/main.tsx`** - Copy from artifact
22. **`frontend/src/App.tsx`** - Copy from artifact
23. **`frontend/src/index.css`** - Copy from artifact

**Create context and services:**

24. **`frontend/src/contexts/AuthContext.tsx`** - Copy from artifact
25. **`frontend/src/services/api.ts`** - Copy from artifact

**Create components:**

26. **`frontend/src/components/Layout.tsx`** - Copy from artifact
27. **`frontend/src/components/LoadingSpinner.tsx`** - Copy from artifact

**Create pages:**

28. **`frontend/src/pages/Login.tsx`** - Copy from artifact
29. **`frontend/src/pages/admin/Users.tsx`** - Copy from artifact
30. **`frontend/src/pages/admin/LeaveTypes.tsx`** - Copy from artifact
31. **`frontend/src/pages/admin/Holidays.tsx`** - Copy from artifact
32. **`frontend/src/pages/manager/PendingRequests.tsx`** - Copy from artifact
33. **`frontend/src/pages/manager/RequestHistory.tsx`** - Copy from artifact
34. **`frontend/src/pages/employee/LeaveBalance.tsx`** - Copy from artifact
35. **`frontend/src/pages/employee/ApplyLeave.tsx`** - Copy from artifact
36. **`frontend/src/pages/employee/RequestHistory.tsx`** - Copy from artifact

**Create test setup:**

37. **`frontend/src/test/setup.ts`** - Copy from artifact

---

## **Phase 4: First Launch**

### **Step 4: Build and Start**
```bash
# From the root directory (leave-management-system/)
docker-compose up --build

# This will:
# 1. Build the API container
# 2. Build the Frontend container
# 3. Start PostgreSQL database
# 4. Start Redis cache
# 5. Start pgAdmin
# 6. Seed demo data
```

### **Step 5: Verify Services**
```bash
# Check all containers are running
docker-compose ps

# Should show 5 services running:
# - leave-management-system_api_1
# - leave-management-system_frontend_1  
# - leave-management-system_leave_db_1
# - leave-management-system_redis_1
# - leave-management-system_pgadmin_1
```

---

## **Phase 5: Test the System**

### **Step 6: Access Applications**

**Frontend Application:**
- URL: http://localhost:5173
- Test login with demo users:
  - Username: `admin` (Admin role)
  - Username: `manager` (Manager role)  
  - Username: `alice` (Employee role)

**API Documentation:**
- URL: http://localhost:8000/docs
- Interactive Swagger UI for API testing

**Health Check:**
- URL: http://localhost:8000/health
- Should return: `{"status": "healthy", "database": "connected", "redis": "connected"}`

**Database Admin (pgAdmin):**
- URL: http://localhost:5050
- Login: admin@example.com / admin123

### **Step 7: Test Key Workflows**

**As Employee (alice):**
1. Login → View Leave Balance
2. Apply for Leave → Submit request
3. Check My Requests → See pending status

**As Manager (manager):**
1. Login → View Pending Requests
2. Approve/Reject → Process employee requests
3. Check History → See all decisions

**As Admin (admin):**
1. Login → Manage Users
2. Create new leave types
3. Add corporate holidays
4. Adjust user balances

---

## **Phase 6: Development Setup (Optional)**

### **Step 8: Local Development**
```bash
# Stop containers
docker-compose down

# Start only dependencies
docker-compose up leave_db redis pgadmin

# Run API locally (in new terminal)
cd api
pip install -r requirements.txt
uvicorn main:app --reload

# Run frontend locally (in another terminal)
cd frontend
npm install
npm run dev
```

---

## **Phase 7: Push to GitHub**

### **Step 9: Create GitHub Repository**
```bash
# Add all files to git
git add .
git commit -m "Initial commit: Production-ready leave management system"

# Create repo on GitHub (replace YOUR_USERNAME)
# Method 1: Using GitHub CLI
gh repo create leave-management-system --public
git remote add origin https://github.com/YOUR_USERNAME/leave-management-system.git
git push -u origin main

# Method 2: Manual
# 1. Go to https://github.com/new
# 2. Create repo named "leave-management-system"
# 3. Copy the git commands GitHub provides
```

---

## **🔧 Troubleshooting**

### **Common Issues:**

**Docker not starting:**
```bash
# Check Docker is running
docker info

# Check ports aren't in use
netstat -tulpn | grep :5173
netstat -tulpn | grep :8000
```

**Database connection errors:**
```bash
# Check database is ready
docker-compose logs leave_db

# Restart if needed
docker-compose restart leave_db
```

**Frontend build errors:**
```bash
# Check Node.js version (need 18+)
node --version

# Clear and rebuild
docker-compose down
docker-compose up --build --force-recreate
```

**File copy errors:**
- Make sure file extensions are correct (.py, .tsx, .ts, .yml)
- Check for hidden characters when copying from artifacts
- Verify directory structure matches exactly

---

## **✅ Success Checklist**

- [ ] All 37 files created with correct content
- [ ] Docker containers all running (5 services)
- [ ] Frontend accessible at http://localhost:5173
- [ ] API docs at http://localhost:8000/docs
- [ ] Can login with demo users (admin, manager, alice)
- [ ] Employee can apply for leave
- [ ] Manager can approve requests
- [ ] Admin can manage users
- [ ] Pushed to GitHub successfully

**🎉 Once complete, you have a fully functional, production-ready leave management system!**

Need help with any specific step? Let me know which phase you're on and any errors you encounter!
