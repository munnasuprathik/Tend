# 🚀 Complete Deployment Checklist - Tend Application

## ✅ Pre-Deployment Verification

### Code Readiness
- [x] All critical bugs fixed
- [x] Production-ready error handling
- [x] Security headers configured
- [x] Rate limiting implemented
- [x] Environment variable validation
- [x] Dynamic URLs (no hardcoded domains)
- [x] CORS properly configured
- [x] Health check endpoint working
- [x] Dockerfile created
- [x] Kubernetes manifests ready (optional)

---

## 📦 Frontend Deployment (Vercel)

### Step 1: Prepare Repository
- [ ] Push code to GitHub
- [ ] Ensure `vercel.json` is in root
- [ ] Verify `frontend/package.json` exists

### Step 2: Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. **Important**: Set **Root Directory** to `frontend`
5. Vercel will auto-detect React app

### Step 3: Configure Environment Variables

Go to: **Project Settings → Environment Variables**

Add these for **Production**, **Preview**, and **Development**:

```bash
# REQUIRED - Backend API URL (get this after backend deployment)
REACT_APP_BACKEND_URL=https://your-backend-url.up.railway.app

# REQUIRED - Clerk Authentication
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_your_key_here

# OPTIONAL - Frontend URL (auto-detected from Vercel URL)
REACT_APP_FRONTEND_URL=https://your-frontend.vercel.app
```

**⚠️ Important**: 
- `REACT_APP_BACKEND_URL` must be set **after** backend is deployed
- Vercel automatically sets `VERCEL_URL` for preview deployments
- Frontend uses `window.location.origin` as fallback (works automatically)

### Step 4: Deploy
- [ ] Click "Deploy"
- [ ] Wait for build to complete
- [ ] Copy your Vercel URL (e.g., `https://maketend.vercel.app`)

---

## 🖥️ Backend Deployment (Railway)

### Step 1: Prepare Repository
- [ ] Ensure `Dockerfile` is in root directory
- [ ] Ensure `railway.json` is in root (optional)
- [ ] Verify `backend/requirements.txt` exists

### Step 2: Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Dockerfile

### Step 3: Configure Environment Variables

Go to: **Service → Variables**

Add these **REQUIRED** variables:

```bash
# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/tend
DB_NAME=tend

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# SMTP Email
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-password
SENDER_EMAIL=your-email@domain.com

# Clerk Authentication
CLERK_SECRET_KEY=sk_live_your_key_here

# Admin Access
ADMIN_SECRET=your-secure-secret-key-here

# Frontend Connection (CRITICAL for CORS)
FRONTEND_URL=https://maketend.vercel.app
CORS_ORIGINS=https://maketend.vercel.app,https://*.vercel.app

# Environment
ENVIRONMENT=production
```

**Optional** variables:
```bash
# Tavily API (for persona research)
TAVILY_API_KEY=your-key

# Email Reply Polling
IMAP_HOST=imap.hostinger.com
INBOX_EMAIL=mail@domain.com
INBOX_PASSWORD=your-password

# Email Domain
EMAIL_DOMAIN=yourdomain.com
```

### Step 4: Deploy
- [ ] Railway will automatically build and deploy
- [ ] Wait for deployment to complete
- [ ] Copy your Railway URL (e.g., `https://your-app.up.railway.app`)

### Step 5: Get Backend URL
1. Go to Railway Dashboard → Your Service
2. Click "Settings" → "Networking"
3. Copy the **Public Domain** (e.g., `https://your-app.up.railway.app`)
4. **This is your backend URL!**

---

## 🔗 Connect Frontend to Backend

### Step 1: Update Frontend Environment Variable

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Find `REACT_APP_BACKEND_URL`
3. Update it with your Railway backend URL:
   ```
   REACT_APP_BACKEND_URL=https://your-app.up.railway.app
   ```
4. **Redeploy** frontend (Vercel will auto-redeploy on env var change)

### Step 2: Update Backend CORS

1. Go to Railway Dashboard → Your Service → Variables
2. Update `CORS_ORIGINS` with your Vercel URL:
   ```
   CORS_ORIGINS=https://maketend.vercel.app,https://*.vercel.app
   ```
3. Update `FRONTEND_URL`:
   ```
   FRONTEND_URL=https://maketend.vercel.app
   ```
4. Railway will automatically restart with new variables

### Step 3: Test Connection

1. Open your frontend URL: `https://your-frontend.vercel.app`
2. Open browser DevTools → Network tab
3. Try to sign in or load dashboard
4. Check if API calls are successful (status 200)
5. If you see CORS errors, check:
   - Backend `CORS_ORIGINS` includes frontend URL
   - Frontend `REACT_APP_BACKEND_URL` is correct

---

## ✅ Post-Deployment Verification

### Backend Health Check
```bash
curl https://your-backend-url.up.railway.app/health
```
Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "openai": "connected",
  "smtp": "configured",
  "version": "2.0"
}
```

### Frontend-Backend Connection Test
1. Open frontend in browser
2. Open DevTools → Console
3. Should see: `🔧 API Configuration: { BACKEND_URL: '...', ... }`
4. Try to sign in
5. Check Network tab for API calls

### Common Issues & Fixes

#### ❌ CORS Error
**Symptom**: `Access-Control-Allow-Origin` error in browser console

**Fix**:
1. Check `CORS_ORIGINS` in Railway includes your Vercel URL
2. Format: `https://your-frontend.vercel.app,https://*.vercel.app`
3. Restart backend service

#### ❌ Backend Not Found
**Symptom**: `404 Not Found` or connection refused

**Fix**:
1. Verify `REACT_APP_BACKEND_URL` in Vercel is correct
2. Check Railway service is running (green status)
3. Test backend URL directly: `curl https://your-backend-url/health`

#### ❌ Environment Variables Not Working
**Symptom**: Frontend shows errors about missing config

**Fix**:
1. In Vercel, ensure env vars are set for **Production**, **Preview**, AND **Development**
2. Redeploy frontend after adding env vars
3. Clear browser cache and hard refresh

---

## 🔐 Security Checklist

- [x] No hardcoded secrets in code
- [x] All secrets in environment variables
- [x] CORS properly configured (not `*` in production)
- [x] Rate limiting enabled
- [x] Security headers configured
- [x] Request size limits set
- [x] Admin authentication required
- [x] Error messages don't leak sensitive info

---

## 📊 Monitoring Setup

### Railway Monitoring
- [ ] Check Railway dashboard for service health
- [ ] Monitor logs for errors
- [ ] Set up alerts for service downtime

### Vercel Monitoring
- [ ] Check Vercel dashboard for build status
- [ ] Monitor analytics (already integrated)
- [ ] Check Speed Insights (already integrated)

### Application Monitoring
- [ ] Test `/health` endpoint regularly
- [ ] Monitor error logs in admin dashboard
- [ ] Check email sending success rate

---

## 🎯 Quick Deployment Summary

### Frontend (Vercel)
1. Push to GitHub
2. Import in Vercel (set root to `frontend`)
3. Add env vars: `REACT_APP_BACKEND_URL`, `REACT_APP_CLERK_PUBLISHABLE_KEY`
4. Deploy
5. Copy Vercel URL

### Backend (Railway)
1. Push to GitHub
2. Import in Railway
3. Add all required env vars (see above)
4. Deploy
5. Copy Railway URL

### Connect Them
1. Update `REACT_APP_BACKEND_URL` in Vercel with Railway URL
2. Update `CORS_ORIGINS` in Railway with Vercel URL
3. Redeploy both
4. Test!

---

## 🚨 Critical Configuration

### Must Match:
- ✅ Backend `CORS_ORIGINS` must include Frontend URL
- ✅ Frontend `REACT_APP_BACKEND_URL` must match Backend URL
- ✅ Backend `FRONTEND_URL` must match Frontend URL (for email links)

### Example Configuration:

**Vercel (Frontend)**:
```
REACT_APP_BACKEND_URL=https://tend-backend.up.railway.app
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_...
```

**Railway (Backend)**:
```
FRONTEND_URL=https://maketend.vercel.app
CORS_ORIGINS=https://maketend.vercel.app,https://*.vercel.app
```

---

## ✅ Final Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway
- [ ] Environment variables configured correctly
- [ ] Frontend connected to backend (no CORS errors)
- [ ] Health check endpoint working
- [ ] Can sign in via Clerk
- [ ] Can access user dashboard
- [ ] Can access admin dashboard
- [ ] Emails sending successfully
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## 🎉 You're Ready!

Once all checkboxes are complete, your application is fully deployed and connected! 🚀

**Need Help?**
- Check logs in Railway dashboard
- Check logs in Vercel dashboard
- Test `/health` endpoint
- Verify environment variables match

