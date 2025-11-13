# How to Run the Backend

## Prerequisites

1. **Python 3.8+** installed
2. **MongoDB** running (local or remote)
3. **Environment variables** configured in `backend/.env`

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Make sure `backend/.env` file exists with:
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `OPENAI_API_KEY` - Your OpenAI API key
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - Email settings
- `ADMIN_SECRET` - Admin authentication secret
- `CORS_ORIGINS` - Allowed CORS origins (use `*` for development)

### 3. Run the Server

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Or use the npm script from root:
```bash
npm run backend
```

## Server Details

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Default Port:** 8000
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc

## Environment Variables

Required variables in `backend/.env`:

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=inboxinspire

# OpenAI
OPENAI_API_KEY=your-api-key-here

# SMTP Email
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-password
SENDER_EMAIL=your-email@domain.com

# Admin
ADMIN_SECRET=your-secret-key

# CORS
CORS_ORIGINS=*
```

## Troubleshooting

1. **Port already in use:** Change port with `--port 8001`
2. **MongoDB connection error:** Check `MONGO_URL` in `.env`
3. **Module not found:** Run `pip install -r requirements.txt`
4. **Environment variables missing:** Check `backend/.env` file exists

