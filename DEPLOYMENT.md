# HussEyquation Deployment Guide

This guide covers deploying the HussEyquation NBA ranking website to production.

## Architecture
- **Frontend**: Next.js 15 → Deploy to **Vercel**
- **Backend**: FastAPI → Deploy to **Railway** 
- **Database**: SQLite (included with backend)

## Step 1: Deploy Backend API (Railway)

1. **Sign up for Railway**: https://railway.app
2. **Create new project** from GitHub repo
3. **Select the `/api` folder** as the root directory
4. **Set environment variables** in Railway dashboard:
   ```
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   DATABASE_PATH=./husseyquation.sqlite
   ENVIRONMENT=production
   ```
5. **Deploy** - Railway will automatically build and deploy

The database will be included in the deployment (already copied by `init_db.py`).

## Step 2: Deploy Frontend (Vercel)

1. **Sign up for Vercel**: https://vercel.com
2. **Import project** from GitHub
3. **Select the `/web` folder** as the root directory
4. **Set environment variables** in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-railway-url.railway.app
   ```
5. **Deploy** - Vercel will build and deploy automatically

## Step 3: Update CORS Settings

After frontend is deployed:
1. Get your Vercel deployment URL
2. Update Railway environment variable:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```
3. Redeploy the backend

## Step 4: Custom Domain (Optional)

### For Frontend (Vercel):
1. Go to Project Settings → Domains
2. Add your custom domain (e.g., `husseyquation.com`)
3. Configure DNS as instructed

### For Backend (Railway):
1. Go to Project → Settings → Domains
2. Add custom domain for API (e.g., `api.husseyquation.com`)
3. Update frontend environment variable to use custom API URL

## Environment Variables Summary

### Backend (Railway):
```bash
CORS_ORIGINS=https://your-domain.com
DATABASE_PATH=./husseyquation.sqlite
ENVIRONMENT=production
```

### Frontend (Vercel):
```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

## Monitoring & Updates

- **Railway**: Provides built-in monitoring and logs
- **Vercel**: Automatic deployments on git push
- **Database Updates**: Upload new CSV files and re-run import scripts

## Cost Estimates
- **Railway**: Free tier available (500 hours/month)
- **Vercel**: Free tier includes 100GB bandwidth
- **Total**: $0-20/month depending on usage

## Troubleshooting

### API Issues:
- Check Railway logs
- Verify CORS_ORIGINS includes frontend domain
- Ensure database file exists

### Frontend Issues:
- Check Vercel deployment logs  
- Verify NEXT_PUBLIC_API_URL is correct
- Test API endpoints directly

## Alternative Deployment Options

### Backend Alternatives:
- **Render**: Similar to Railway
- **Heroku**: More expensive but stable
- **AWS/GCP**: More complex setup

### Frontend Alternatives:
- **Netlify**: Similar to Vercel
- **AWS Amplify**: If using AWS ecosystem
- **GitHub Pages**: Static only (would need different API approach)