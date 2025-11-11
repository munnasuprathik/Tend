# InboxInspire - Complete Setup Guide

## 🎯 Overview

InboxInspire is an AI-powered motivational email platform that delivers personalized inspiration directly to users' inboxes, styled after famous personalities or custom tones.

---

## ✨ Key Features Implemented

### 1. **Magic Link Authentication**
- Passwordless login via email
- Secure token-based verification
- Automatic new user onboarding flow

### 2. **4-Step Onboarding**
- Step 1: Name collection
- Step 2: Goals & aspirations
- Step 3: Personality/tone selection (Famous figures, Tones, or Custom)
- Step 4: Schedule configuration (frequency & time)

### 3. **Advanced AI Personalization**
- **GPT-4o powered** message generation
- Deep personality matching with enhanced prompts
- Messages truly feel like they're from the selected personality
- Context-aware based on user goals
- Personalized with user's name

### 4. **User Dashboard**
- View current settings
- Edit all preferences
- Generate preview messages
- Send instant motivation
- Toggle active/inactive status

### 5. **Admin Dashboard**
- Real-time statistics (total users, active users, emails sent, success rate)
- User management view
- Email logs monitoring
- Secure admin authentication

### 6. **SMTP Email Integration**
- Hostinger SMTP configured
- Beautiful HTML email templates
- Email logging for monitoring
- Scheduled daily delivery at 9 AM

---

## 🔧 Technical Stack

**Backend:**
- FastAPI (Python)
- MongoDB (user data, email logs)
- OpenAI GPT-4o (message generation)
- APScheduler (automated email scheduling)
- aiosmtplib (SMTP email delivery)

**Frontend:**
- React 19
- Shadcn UI components
- Tailwind CSS
- Axios
- Space Grotesk + Inter fonts

---

## 🔐 Environment Variables

All configured in `/app/backend/.env`:

```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database

# OpenAI
OPENAI_API_KEY=sk-proj-mGz_Srk-...

# SMTP (Hostinger)
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USERNAME=mail@quiccle.com
SMTP_PASSWORD=Munna@mail1234
SENDER_EMAIL=mail@quiccle.com

# Admin
ADMIN_SECRET=admin_secure_pass_2024

# CORS
CORS_ORIGINS=*
```

---

## 📧 Email Configuration

### SMTP Details (Hostinger)
- **Host:** smtp.hostinger.com
- **Port:** 465
- **Encryption:** SSL/TLS
- **Username:** mail@quiccle.com
- **Password:** Munna@mail1234

### Email Types Sent:
1. **Magic Link Login** - Passwordless authentication
2. **Daily Motivation** - Scheduled personalized messages
3. **Instant Send** - On-demand motivation from dashboard

---

## 🎭 Personality Options

### Famous Personalities:
- Elon Musk
- Steve Jobs
- A.P.J. Abdul Kalam
- Oprah Winfrey
- Nelson Mandela
- Maya Angelou
- Tony Robbins
- Brené Brown
- Simon Sinek
- Michelle Obama
- Warren Buffett
- Richard Branson

### Tone Styles:
- Funny & Uplifting
- Friendly & Warm
- Roasting (Tough Love)
- Serious & Direct
- Philosophical & Deep
- Energetic & Enthusiastic
- Calm & Meditative
- Poetic & Artistic

### Custom:
Users can describe their own preferred style

---

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/login` - Send magic link
- `POST /api/auth/verify` - Verify token

### User Management
- `POST /api/onboarding` - Complete new user setup
- `GET /api/users/{email}` - Get user profile
- `PUT /api/users/{email}` - Update user settings

### Messaging
- `POST /api/generate-message` - Generate AI message preview
- `POST /api/send-now/{email}` - Send instant motivation

### Admin (requires Bearer token)
- `GET /api/admin/stats` - Platform statistics
- `GET /api/admin/users` - All users list
- `GET /api/admin/email-logs` - Email delivery logs

---

## 🎨 Design Features

### UI/UX:
- Clean, modern interface
- Soft gradient backgrounds (blue/gray palette)
- Smooth animations and transitions
- Fully responsive design
- Progress indicators for onboarding
- Toast notifications for feedback

### Typography:
- **Headings:** Space Grotesk
- **Body:** Inter

### Color Scheme:
- Primary: Blue to Indigo gradient
- Background: Soft gray gradient
- Success: Green
- Error: Red

---

## 📊 Admin Access

**URL:** `https://aipep.preview.emergentagent.com/admin`

**Admin Token:** `admin_secure_pass_2024`

Features:
- View total/active users
- Monitor email success rate
- Review all users and their settings
- Check email delivery logs
- Real-time statistics

---

## ⏰ Scheduled Jobs

**Daily Motivation Delivery:**
- Runs every day at 9:00 AM
- Sends personalized messages to all active users
- Uses APScheduler with CronTrigger
- Logs all email attempts

---

## 🧪 Testing

### Manual Testing:
1. Visit main page and enter email
2. Check email for magic link
3. Complete 4-step onboarding
4. Access dashboard and test features
5. Generate preview messages
6. Send instant motivation

### API Testing:
```bash
# Test message generation
curl -X POST "${API}/generate-message" \\
  -H "Content-Type: application/json" \\
  -d '{
    "goals": "Building a startup",
    "personality": {"type": "famous", "value": "Elon Musk"},
    "user_name": "Alex"
  }'

# Test instant send
curl -X POST "${API}/send-now/user@example.com"

# Test admin stats
curl -X GET "${API}/admin/stats" \\
  -H "Authorization: Bearer admin_secure_pass_2024"
```

---

## 🎯 Key Improvements Made

1. **Enhanced AI Prompts:**
   - Deep personality matching
   - Specific tone instructions for each style
   - Context-aware message generation
   - Temperature set to 0.8 for creative yet consistent output

2. **Complete Flow Redesign:**
   - Magic link authentication (no passwords)
   - Name collection first
   - Streamlined onboarding
   - Full-featured dashboard

3. **SMTP Integration:**
   - Replaced SendGrid with Hostinger SMTP
   - Working email delivery
   - Email logging for monitoring

4. **Admin Panel:**
   - Comprehensive monitoring
   - User management
   - Email log tracking
   - Real-time statistics

5. **Improved UI:**
   - Better visual hierarchy
   - Smooth animations
   - Enhanced accessibility
   - Responsive design

---

## 📝 Usage Flow

1. **User enters email** → Receives magic link
2. **Clicks magic link** → Enters name
3. **Onboarding** → Goals → Personality → Schedule
4. **Dashboard** → View/edit settings, preview messages, send now
5. **Scheduled emails** → Delivered daily at configured time
6. **Admin** → Monitors all activity

---

## 🔒 Security

- Magic link tokens (cryptographically secure)
- Admin authentication with Bearer tokens
- No password storage
- CORS configured
- SSL/TLS email encryption

---

## 📞 Support

For any issues or questions, check:
- Backend logs: `/var/log/supervisor/backend.*.log`
- MongoDB collections: `users`, `email_logs`, `pending_logins`
- Email delivery status in admin panel

---

## 🎉 Success Metrics

The system tracks:
- Total users
- Active vs inactive users
- Total emails sent
- Failed email deliveries
- Email success rate percentage
- Last email sent timestamp per user

---

**Built with ❤️ using FastAPI, React, and GPT-4o**
