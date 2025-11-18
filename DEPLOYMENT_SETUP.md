# Deployment Setup Guide - Tend

## 🏗️ Architecture

- **Frontend**: Vercel (React SPA)
- **Backend**: VM/Server (FastAPI)
- **Connection**: Dynamic API URLs via environment variables

---

## 📦 Frontend Setup (Vercel)

### 1. Install Dependencies

```bash
cd frontend
npm install @vercel/analytics @vercel/speed-insights --legacy-peer-deps
```

### 2. Environment Variables in Vercel Dashboard

Go to: **Vercel Project → Settings → Environment Variables**

Add these variables for **Production**, **Preview**, and **Development**:

```
REACT_APP_BACKEND_URL=https://api.maketend.com
REACT_APP_FRONTEND_URL=https://maketend.com
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_your_key_here
```

**Note**: Vercel automatically sets `VERCEL_URL` for preview deployments.

### 3. Deploy

**Option A: Via Vercel CLI**
```bash
npm i -g vercel
cd frontend
vercel
```

**Option B: Via GitHub (Recommended)**
1. Push code to GitHub
2. Import project in Vercel
3. Set root directory to `frontend`
4. Vercel will auto-deploy on push

### 4. Vercel Configuration

The `vercel.json` file is configured with:
- ✅ Build command: `cd frontend && npm install && npm run build`
- ✅ Output directory: `frontend/build`
- ✅ SPA routing (all routes → index.html)
- ✅ Security headers

---

## 🖥️ Backend Setup (VM)

### 1. Environment Variables

Create `.env` file on your VM:

```bash
# MongoDB (required)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/

# Database Name (optional)
DB_NAME=tend

# OpenAI (required)
OPENAI_API_KEY=sk-your-key-here

# SMTP (required)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# Frontend URL (required for CORS and email links)
FRONTEND_URL=https://maketend.com

# CORS Origins (required for Vercel)
# Allows production domain + all Vercel preview deployments
CORS_ORIGINS=https://maketend.com,https://www.maketend.com,*.vercel.app

# Admin Secret (required)
ADMIN_SECRET=your-secure-secret-here

# Environment (optional)
ENVIRONMENT=production

# Optional: Tavily API
TAVILY_API_KEY=your-key

# Optional: Email Reply Polling
IMAP_HOST=imap.gmail.com
INBOX_EMAIL=your-inbox@gmail.com
INBOX_PASSWORD=your-app-password
```

### 2. CORS Configuration

The backend now supports:
- ✅ Multiple origins (comma-separated)
- ✅ Vercel preview deployments (`*.vercel.app` pattern)
- ✅ Automatic localhost in development

**CORS_ORIGINS Format:**
```
CORS_ORIGINS=https://maketend.com,https://www.maketend.com,*.vercel.app
```

This allows:
- Production domain
- All Vercel preview deployments (automatic)
- All Vercel branch deployments (automatic)

### 3. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start Backend Server

**Development:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Production (with systemd):**
```bash
# Create service file
sudo nano /etc/systemd/system/tend-api.service
```

```ini
[Unit]
Description=Tend API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/backend/.env
ExecStart=/path/to/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable tend-api
sudo systemctl start tend-api
sudo systemctl status tend-api
```

### 5. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.maketend.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (handled by backend, but can add here too)
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Credentials true always;
    }
}
```

**SSL Setup (Let's Encrypt):**
```bash
sudo certbot --nginx -d api.maketend.com
```

---

## 🔗 Dynamic URL Configuration

### Frontend (`frontend/src/config/api.js`)

Automatically detects environment:
1. **Explicit**: `REACT_APP_BACKEND_URL` (highest priority)
2. **Vercel**: `VERCEL_BACKEND_URL` (if set)
3. **Development**: `http://localhost:8000`
4. **Production**: `https://api.maketend.com`

### Backend CORS

Dynamic origin checking:
- Checks exact matches first
- Supports `*.vercel.app` pattern (allows all Vercel previews)
- Automatically allows localhost in development

---

## 📊 Vercel Analytics

Analytics and Speed Insights are automatically included:

```jsx
// Added in frontend/src/index.js
<Analytics />
<SpeedInsights />
```

**Tracked:**
- Page views
- Performance metrics
- Core Web Vitals
- User interactions

---

## 🧪 Testing

### Local Development

**Frontend:**
```bash
cd frontend
REACT_APP_BACKEND_URL=http://localhost:8000 npm start
```

**Backend:**
```bash
cd backend
CORS_ORIGINS=http://localhost:3000 uvicorn server:app --reload
```

### Production Testing

1. Deploy frontend to Vercel
2. Set environment variables
3. Test API connection: `curl https://api.maketend.com/api/health`
4. Check browser console for CORS errors
5. Test sign-in/sign-up flow

---

## 🔍 Troubleshooting

### CORS Errors

**Problem**: `Access-Control-Allow-Origin` errors

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure `*.vercel.app` is included for preview deployments
3. Verify frontend URL matches one in `CORS_ORIGINS`
4. Check backend logs for origin validation

### API Connection Failed

**Problem**: Frontend can't reach backend

**Solution**:
1. Verify `REACT_APP_BACKEND_URL` in Vercel environment variables
2. Test backend directly: `curl https://api.maketend.com/api/health`
3. Check backend is running: `sudo systemctl status tend-api`
4. Verify firewall allows port 8000 (or 443 if using Nginx)

### Environment Variables Not Loading

**Problem**: Variables not working in Vercel

**Solution**:
1. Variables must start with `REACT_APP_` for Create React App
2. Redeploy after adding variables (Vercel doesn't auto-reload)
3. Check build logs in Vercel dashboard
4. Verify variable names match exactly

---

## 📝 Environment Variables Summary

### Frontend (Vercel)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Yes | Backend API URL | `https://api.maketend.com` |
| `REACT_APP_FRONTEND_URL` | No | Frontend URL (auto-detected) | `https://maketend.com` |
| `REACT_APP_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key | `pk_live_...` |
| `VERCEL_URL` | Auto | Vercel deployment URL | `tend-abc123.vercel.app` |

### Backend (VM)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGO_URL` | Yes | MongoDB connection string | `mongodb+srv://...` |
| `OPENAI_API_KEY` | Yes | OpenAI API key | `sk-...` |
| `SMTP_HOST` | Yes | SMTP server | `smtp.gmail.com` |
| `SMTP_USERNAME` | Yes | SMTP username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Yes | SMTP password/app password | `...` |
| `FRONTEND_URL` | Yes | Frontend URL for email links | `https://maketend.com` |
| `CORS_ORIGINS` | Yes | Allowed origins (comma-separated) | `https://maketend.com,*.vercel.app` |
| `ADMIN_SECRET` | Yes | Admin authentication secret | `...` |
| `ENVIRONMENT` | No | Environment name | `production` |

---

## ✅ Deployment Checklist

### Frontend (Vercel)
- [ ] Dependencies installed (`@vercel/analytics`, `@vercel/speed-insights`)
- [ ] Environment variables set in Vercel
- [ ] `vercel.json` configured
- [ ] Deployed and accessible
- [ ] Analytics tracking working

### Backend (VM)
- [ ] Environment variables configured (`.env` file)
- [ ] Dependencies installed
- [ ] Backend server running
- [ ] CORS configured with `*.vercel.app` pattern
- [ ] Reverse proxy configured (Nginx)
- [ ] SSL certificate installed (HTTPS)
- [ ] Health check endpoint working
- [ ] Systemd service configured (optional)

### Testing
- [ ] Frontend loads correctly
- [ ] API calls work from frontend
- [ ] CORS headers present
- [ ] Sign-in/sign-up flow works
- [ ] Onboarding flow works
- [ ] User dashboard loads
- [ ] Admin dashboard accessible
- [ ] Analytics tracking data visible

---

## 🎯 URL Structure

### Production
- **Frontend**: `https://maketend.com`
- **Backend API**: `https://api.maketend.com`

### Vercel Preview Deployments
- **Frontend**: `https://tend-abc123.vercel.app` (automatic)
- **Backend API**: `https://api.maketend.com` (same)

### Development
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`

---

## 🔐 Security Notes

1. **CORS**: Only allow trusted origins in production
2. **Environment Variables**: Never commit `.env` files
3. **Admin Secret**: Use strong, random secret
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Already configured in backend

---

**Last Updated**: 2024-01-05

