# 🚀 HussEyquation Deployment Guide

Complete guide to deploy the NBA Player Rankings application to production.

## 🏗️ Architecture Overview

- **Frontend**: Next.js 15 → Vercel
- **Backend**: FastAPI → Railway
- **Database**: PostgreSQL → Railway
- **Domain**: Custom domain (optional)

---

## 📋 Prerequisites

1. **GitHub Account** (for code repository)
2. **Vercel Account** (free tier sufficient)  
3. **Railway Account** (free tier with $5 monthly credit)

---

## 🎯 Deployment Steps

### 1️⃣ Push Code to GitHub

First, ensure your code is in a GitHub repository:

```bash
# If you haven't created the GitHub repo yet:
cd "C:\code\hussEyquation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hussEyquation.git
git push -u origin main
```

### 2️⃣ Deploy Backend to Railway

1. **Go to [railway.app](https://railway.app)** and sign in with GitHub
2. **Create new project** → "Deploy from GitHub repo"
3. **Select your hussEyquation repository**
4. **Railway will auto-detect the configuration** from `railway.toml`
5. **Add PostgreSQL database**:
   - In your Railway project dashboard
   - Click "Add Service" → "Database" → "PostgreSQL"
6. **Configure environment variables**:
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}  # Auto-connected
   CORS_ORIGINS = https://*.vercel.app,http://localhost:3000
   PORT = 8000
   ```
7. **Deploy will start automatically** - wait for completion
8. **Copy your API URL** (e.g., `https://your-api.railway.app`)

### 3️⃣ Deploy Frontend to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Import project** → Select your GitHub repository
3. **Configure build settings**:
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: `web`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
4. **Set environment variables**:
   ```
   NEXT_PUBLIC_API_URL = https://your-api.railway.app
   ```
5. **Deploy** - Vercel will build and deploy automatically
6. **Copy your frontend URL** (e.g., `https://your-app.vercel.app`)

### 4️⃣ Update CORS Settings

1. **Go back to Railway** → Your API service → Variables
2. **Update CORS_ORIGINS**:
   ```
   CORS_ORIGINS = https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000
   ```
3. **Redeploy** your Railway service

### 5️⃣ Initialize Database (One-time)

1. **SSH into Railway container** (or use Railway CLI):
   ```bash
   railway login
   railway link YOUR_PROJECT_ID
   railway run python init_db.py
   ```

2. **Or run initialization script** via Railway dashboard:
   - Go to your API service → Deployments
   - Find latest deployment → View logs
   - Look for initialization messages

---

## 🔧 Configuration Files Created

### `web/vercel.json`
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  }
}
```

### `railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
numReplicas = 1

[[services]]
name = "api"
source = "api/"

[services.variables]
PORT = "8000"
DATABASE_URL = "${{Postgres.DATABASE_URL}}"
CORS_ORIGINS = "https://*.vercel.app"
```

### `api/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🌐 Custom Domain (Optional)

### For Vercel (Frontend):
1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your custom domain (e.g., `husseyquation.com`)
3. Follow DNS configuration instructions

### For Railway (API):
1. Go to Railway dashboard → Your API service → Settings
2. Add custom domain (e.g., `api.husseyquation.com`) 
3. Update CORS settings and frontend API URL

---

## 📊 Monitoring & Maintenance

### Health Checks
- **API Health**: `https://your-api.railway.app/health`
- **Frontend**: Vercel provides built-in monitoring

### Logs
- **Railway**: Dashboard → Service → Logs
- **Vercel**: Dashboard → Project → Functions → View logs

### Database Management
- **Railway PostgreSQL**: Built-in web interface
- **Backup**: Railway provides automatic backups

---

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**:
   - Check CORS_ORIGINS includes your Vercel domain
   - Ensure no trailing slashes in URLs

2. **Database Connection**:
   - Verify DATABASE_URL is properly set
   - Check Railway PostgreSQL service is running

3. **Build Failures**:
   - Verify all dependencies in requirements.txt
   - Check Railway logs for specific error messages

4. **Frontend API Calls Failing**:
   - Confirm NEXT_PUBLIC_API_URL is correct
   - Check Railway API service is healthy

### Support:
- **Railway**: [railway.app/help](https://railway.app/help)
- **Vercel**: [vercel.com/support](https://vercel.com/support)

---

## ✅ Post-Deployment Checklist

- [ ] Backend API health check responds
- [ ] Frontend loads correctly
- [ ] Rankings data displays properly
- [ ] Filtering system works
- [ ] Mobile responsiveness confirmed
- [ ] Performance testing completed
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificates active
- [ ] Monitoring alerts set up

---

🎉 **Congratulations!** Your HussEyquation NBA Rankings app is now live!

**Frontend**: https://your-app.vercel.app  
**API**: https://your-api.railway.app  
**Status**: https://your-api.railway.app/health