# Fly.io Deployment Guide for Mimanasa Backend

## Method 1: Deploy via Fly.io Website (Recommended for Beginners)

### Step 1: Test Docker Locally First

Before deploying, test your Docker container locally:

```bash
cd backend

# Build Docker image
docker build -t mimanasa-backend .

# Run container locally
docker run -p 8000:8000 --env-file .env mimanasa-backend
```

Visit `http://localhost:8000/api/` to verify it works.

Or use docker-compose (easier):

```bash
cd backend
docker-compose up --build
```

Visit `http://localhost:8000/api/` to test.

### Step 2: Create Fly.io Account

1. Go to https://fly.io/
2. Click "Sign Up" (top right)
3. Sign up with GitHub or Email
4. Verify your email

### Step 3: Push Code to GitHub

Make sure your backend code is pushed to GitHub:

```bash
cd backend
git add .
git commit -m "Add Fly.io deployment files"
git push
```

### Step 4: Deploy via Fly.io Dashboard

1. **Login to Fly.io Dashboard**: https://fly.io/dashboard

2. **Create New App**:
   - Click "Create App" or "Launch"
   - Choose "Deploy from GitHub" or "Deploy from Dockerfile"

3. **Connect GitHub Repository**:
   - Select your repository: `MimamsaBackend` (or your repo name)
   - Select branch: `main`
   - Set root directory: `/` (or leave blank if backend is at root)

4. **Configure App**:
   - **App Name**: `mimanasa-backend` (or your choice)
   - **Region**: Choose closest to users (e.g., Singapore, Mumbai, etc.)
   - **Dockerfile Path**: `Dockerfile`

5. **Add PostgreSQL Database**:
   - **Option A: Use Your Existing Neon Database** (Recommended - Already configured)
     - Your `.env` already has Neon DATABASE_URL
     - Just add it as a secret in Fly.io dashboard
     - Go to "Secrets" and add:
       ```
       DATABASE_URL = postgresql://neondb_owner:npg_eEakgslq5z0I@ep-dawn-mountain-ah6x6xtc-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
       ```
   
   - **Option B: Create New Fly.io PostgreSQL** (Alternative)
     - In dashboard, go to your app
     - Click "Add-ons" or "Postgres"
     - Click "Create Postgres"
     - Choose "Development" (Free tier - 1GB)
     - Database will auto-connect via `DATABASE_URL`

6. **Set Environment Variables**:
   - Go to your app dashboard
   - Click "Secrets" or "Environment Variables"
   - Add these secrets:

   ```
   SECRET_KEY = your-django-secret-key-here
   DEBUG = False
   ALLOWED_HOSTS = mimanasa-backend.fly.dev
   CORS_ALLOWED_ORIGINS = https://your-frontend.vercel.app,https://your-frontend.netlify.app
   DATABASE_URL = postgresql://username:password@host/database?sslmode=require
   CLOUDINARY_CLOUD_NAME = your_cloud_name
   CLOUDINARY_API_KEY = your_api_key
   CLOUDINARY_API_SECRET = your_api_secret
   EMAIL_HOST_PASSWORD = your_brevo_api_key
   DEFAULT_FROM_EMAIL = your_email@example.com
   ```

7. **Deploy**:
   - Click "Deploy" button
   - Wait 2-5 minutes for build to complete
   - Your app will be live at: `https://mimanasa-backend.fly.dev`

### Step 5: Run Database Migrations

After first deployment:

1. Go to your app dashboard
2. Click "Console" or "SSH"
3. Run these commands:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. Type `exit` to close console

### Step 6: Verify Deployment

Visit these URLs:
- API: `https://mimanasa-backend.fly.dev/api/`
- Admin: `https://mimanasa-backend.fly.dev/admin/`

---

## Method 2: Deploy via CLI (Advanced)

### Prerequisites

1. Install Fly.io CLI:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. Login:
   ```bash
   fly auth login
   ```

### Deployment Steps

```bash
cd backend

# Launch app (first time)
fly launch --no-deploy

# Set secrets
fly secrets set SECRET_KEY="your-secret-key"
fly secrets set DEBUG="False"
fly secrets set CLOUDINARY_CLOUD_NAME="your-cloud-name"
fly secrets set CLOUDINARY_API_KEY="your-api-key"
fly secrets set CLOUDINARY_API_SECRET="your-api-secret"
fly secrets set EMAIL_HOST_PASSWORD="your-brevo-api-key"
fly secrets set DEFAULT_FROM_EMAIL="your-email@example.com"

# Deploy
fly deploy

# Run migrations
fly ssh console
python manage.py migrate
python manage.py createsuperuser
exit
```

## Important URLs

- **App URL**: `https://mimanasa-backend.fly.dev`
- **API URL**: `https://mimanasa-backend.fly.dev/api/`
- **Admin Panel**: `https://mimanasa-backend.fly.dev/admin/`

## Update Frontend Environment Variables

After deployment, update your frontend `.env.production`:

```env
VITE_API_BASE_URL=https://mimanasa-backend.fly.dev/api
```

## Common Commands

```bash
# View logs
fly logs

# SSH into container
fly ssh console

# Scale app
fly scale vm shared-cpu-1x --memory 512

# Check app status
fly status

# Open app in browser
fly open

# Restart app
fly apps restart mimanasa-backend

# View secrets
fly secrets list

# Deploy new version
fly deploy
```

## Database Management

```bash
# Connect to PostgreSQL
fly postgres connect -a <postgres-app-name>

# Create database backup
fly postgres backup create -a <postgres-app-name>

# List backups
fly postgres backup list -a <postgres-app-name>
```

## Troubleshooting

### 1. App not starting
```bash
fly logs
# Check for errors in logs
```

### 2. Database connection issues
```bash
fly secrets list
# Verify DATABASE_URL is set
```

### 3. Static files not loading
```bash
fly ssh console
python manage.py collectstatic --noinput
exit
```

### 4. CORS errors
```bash
# Update CORS_ALLOWED_ORIGINS secret
fly secrets set CORS_ALLOWED_ORIGINS="https://your-frontend.com"
```

## Cost Optimization

- Free tier includes: 3 shared-cpu-1x VMs with 256MB RAM
- PostgreSQL: Free "Development" tier (1GB storage)
- Upgrade only if needed

## Security Checklist

- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY
- ✅ Proper ALLOWED_HOSTS
- ✅ CORS configured correctly
- ✅ Database credentials secured
- ✅ Environment variables in secrets

## Monitoring

```bash
# Real-time logs
fly logs -a mimanasa-backend

# App metrics
fly dashboard
```

## Rollback

```bash
# List releases
fly releases

# Rollback to previous version
fly releases rollback <version-number>
```

## Custom Domain (Optional)

```bash
# Add custom domain
fly certs add yourdomain.com

# Get DNS records to configure
fly certs show yourdomain.com
```

Then add the provided DNS records to your domain registrar.

## Support

- Fly.io Docs: https://fly.io/docs/
- Community: https://community.fly.io/
