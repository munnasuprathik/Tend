# ⚡ Quick Deployment Guide - 5 Minutes

## 🎯 Simple 3-Step Deployment

### Step 1: Deploy Backend (Railway) - 2 minutes

1. Go to [railway.app](https://railway.app) → New Project → GitHub
2. Select your repository
3. Add environment variables (copy from `DEPLOYMENT_CHECKLIST.md`)
4. Railway auto-deploys → Copy the URL (e.g., `https://xxx.up.railway.app`)

### Step 2: Deploy Frontend (Vercel) - 2 minutes

1. Go to [vercel.com](https://vercel.com) → New Project → GitHub
2. Select your repository
3. **Set Root Directory to `frontend`**
4. Add environment variables:
   ```
   REACT_APP_BACKEND_URL=https://xxx.up.railway.app  (from Step 1)
   REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_...
   ```
5. Deploy → Copy the URL (e.g., `https://xxx.vercel.app`)

### Step 3: Connect Them - 1 minute

1. **In Railway**: Update `CORS_ORIGINS` with your Vercel URL
2. **In Railway**: Update `FRONTEND_URL` with your Vercel URL
3. **In Vercel**: Update `REACT_APP_BACKEND_URL` with your Railway URL
4. Both auto-redeploy → Done! ✅

---

## 🔗 Connection Formula

```
Frontend (Vercel)                    Backend (Railway)
─────────────────                    ─────────────────
REACT_APP_BACKEND_URL          →     CORS_ORIGINS
  = Railway URL                      = Vercel URL
                                      FRONTEND_URL
                                        = Vercel URL
```

**They must match each other!**

---

## ✅ Test It Works

1. Open your Vercel URL
2. Open DevTools → Network tab
3. Sign in
4. Check API calls return 200 (not CORS errors)

**If CORS errors**: Check that `CORS_ORIGINS` in Railway includes your Vercel URL.

---

## 🎉 That's It!

Your app is live! See `DEPLOYMENT_CHECKLIST.md` for detailed configuration.

