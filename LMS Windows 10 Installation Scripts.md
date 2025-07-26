# LMS Windows 10 Installation Scripts

## Prerequisites

Before running the installation scripts, make sure you have:

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure it's running before executing the script

2. **Git** installed
   - Download from: https://git-scm.com/downloads
   - Make sure it's available in your PATH

## Installation Options

You have two script options:

### Option 1: PowerShell Script (Recommended)
- **File**: `setup_lms_windows.ps1`
- **Best for**: Windows 10/11 with PowerShell
- **Features**: Better error handling, port conflict detection, automatic browser opening

### Option 2: Batch File
- **File**: `setup_lms_windows.bat`
- **Best for**: Command Prompt users or older Windows systems
- **Features**: Compatible with all Windows versions

## How to Run

### Method 1: PowerShell (Recommended)

1. **Download** `setup_lms_windows.ps1` to your desired folder
2. **Right-click** on the file and select "Run with PowerShell"
   
   OR
   
3. **Open PowerShell** in the folder and run:
   ```powershell
   .\setup_lms_windows.ps1
   ```

   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
   .\setup_lms_windows.ps1
   ```

### Method 2: Command Prompt

1. **Download** `setup_lms_windows.bat` to your desired folder
2. **Double-click** the file to run it
   
   OR
   
3. **Open Command Prompt** in the folder and run:
   ```cmd
   setup_lms_windows.bat
   ```

## What the Scripts Do

1. ✅ **Check Prerequisites** - Verify Docker, Git are installed
2. 🔍 **Port Conflict Detection** - Automatically use alternative ports if needed
3. 📥 **Clone Repository** - Download LMS from GitHub
4. 📁 **Organize Files** - Create proper directory structure
5. 🐳 **Create Docker Config** - Generate docker-compose.yml and Dockerfiles
6. 🔧 **Fix Import Issues** - Resolve database import problems
7. 🚀 **Start Application** - Build and run all containers
8. 🧪 **Health Check** - Verify everything is working

## After Installation

The scripts will show you:

- **Frontend**: http://localhost:5173 (or 5174 if port conflict)
- **API**: http://localhost:8000 (or 8001 if port conflict)
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:5050 (or 5051 if port conflict)

### Demo Users

- **Admin**: username `admin`, password `admin123`
- **Manager**: username `manager`, password `manager123`
- **Employee**: username `alice`, password `alice123`

## Troubleshooting

### Docker Issues
```cmd
# Make sure Docker Desktop is running
# Check Docker status
docker --version
docker-compose --version
```

### Port Conflicts
The scripts automatically detect port conflicts and use alternative ports:
- Frontend: 5174 instead of 5173
- API: 8001 instead of 8000
- Database: 5433 instead of 5432
- Redis: 6380 instead of 6379
- pgAdmin: 5051 instead of 5050

### Permission Issues
If you get permission errors:
1. Run PowerShell or Command Prompt as Administrator
2. Make sure Docker Desktop is running
3. Check Windows Defender/Antivirus isn't blocking the scripts

### Stopping the Application
```cmd
cd LMS
docker-compose down
```

### Viewing Logs
```cmd
cd LMS
docker-compose logs -f
```

## Manual Cleanup

If you need to completely remove everything:

```cmd
cd LMS
docker-compose down -v
cd ..
rmdir /s LMS
docker system prune -a
```

## Support

If you encounter issues:
1. Make sure Docker Desktop is running
2. Check that ports aren't being used by other applications
3. Try running the script as Administrator
4. Check Windows Firewall settings

