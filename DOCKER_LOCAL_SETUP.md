# Docker Local Setup Guide

## Prerequisites

1. **Install Docker Desktop**:
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Open Docker Desktop and make sure it's running

2. **Verify Installation**:
   ```bash
   docker --version
   docker-compose --version
   ```

## Quick Start (Using Docker Compose)

### 1. Prepare Environment File

Make sure your `.env` file exists in the `backend` folder with these variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email (Brevo)
EMAIL_HOST_PASSWORD=your-brevo-api-key
DEFAULT_FROM_EMAIL=your-email@example.com
```

### 2. Build and Run

```bash
cd backend

# Build and start container
docker-compose up --build
```

This will:
- Build Django backend container
- Connect to your Neon PostgreSQL database (cloud)
- Run migrations automatically
- Start server on http://localhost:8000

**Note**: This setup uses your Neon cloud database (already configured in `.env`), so you don't need a local PostgreSQL installation.

### 3. Access the Application

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

### 4. Create Superuser (First Time Only)

Open a new terminal while containers are running:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create admin account.

### 5. Stop Container

```bash
# Stop container (Ctrl+C in the running terminal)
# Or in another terminal:
docker-compose down
```

---

## Manual Docker Commands (Without Compose)

### 1. Build Docker Image

```bash
cd backend
docker build -t mimanasa-backend .
```

### 2. Run Container

```bash
docker run -p 8000:8000 --env-file .env mimanasa-backend
```

### 3. Stop Container

```bash
# Find container ID
docker ps

# Stop container
docker stop <container-id>
```

---

## Useful Docker Commands

### View Running Containers
```bash
docker ps
```

### View All Containers (including stopped)
```bash
docker ps -a
```

### View Logs
```bash
# Docker Compose
docker-compose logs -f web

# Single Container
docker logs -f mimanasa-backend
```

### Execute Commands in Container
```bash
# Docker Compose
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Single Container
docker exec -it mimanasa-backend python manage.py migrate
```

### Access Container Shell
```bash
# Docker Compose
docker-compose exec web bash

# Single Container
docker exec -it mimanasa-backend bash
```

### Rebuild Containers
```bash
# Rebuild after code changes
docker-compose up --build

# Force rebuild (no cache)
docker-compose build --no-cache
docker-compose up
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all unused data
docker system prune -a

# Remove specific image
docker rmi mimanasa-backend
```

---

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Database Connection Error

```bash
# Restart containers
docker-compose down
docker-compose up
```

### Permission Errors

Run Docker Desktop as Administrator.

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Static Files Not Loading

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

---

## Development Workflow

### 1. Start Development
```bash
docker-compose up
```

### 2. Make Code Changes
- Edit files in your editor
- Changes are reflected automatically (volume mounted)

### 3. Run Migrations After Model Changes
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 4. Test API
Use Postman or browser to test: http://localhost:8000/api/

### 5. Stop Development
```bash
docker-compose down
```

---

## Production Testing

To test production-like environment locally:

1. Update `.env`:
   ```env
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

2. Rebuild and run:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. Test thoroughly before deploying to Fly.io

---

## Next Steps

After testing locally:
1. Push code to GitHub
2. Follow `FLY_DEPLOYMENT.md` to deploy to Fly.io
3. Update frontend `.env.production` with Fly.io URL
