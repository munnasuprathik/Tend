# Email Reply System Setup Guide

## 🔴 **Issue: Replies Not Being Read**

The email reply system requires **IMAP access** to your email inbox to read user replies. Here's what needs to be configured:

## ✅ **Required Setup**

### 1. **Install Required Package**
```bash
pip install imap-tools beautifulsoup4
```

### 2. **Environment Variables** (Add to `.env` file)

You need to add these three environment variables:

```env
# IMAP Configuration for Email Reply Polling
IMAP_HOST=imap.gmail.com
INBOX_EMAIL=your-inbox@gmail.com
INBOX_PASSWORD=your-app-password
```

### 3. **Gmail Setup (If using Gmail)**

For Gmail, you need to:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "InboxInspire" as the name
   - Copy the 16-character password
   - Use this password (not your regular Gmail password) in `INBOX_PASSWORD`

3. **IMAP Settings**:
   - IMAP must be enabled in Gmail settings
   - Go to: Gmail Settings → Forwarding and POP/IMAP → Enable IMAP

### 4. **Other Email Providers**

**Outlook/Hotmail:**
```env
IMAP_HOST=outlook.office365.com
INBOX_EMAIL=your-email@outlook.com
INBOX_PASSWORD=your-password
```

**Yahoo:**
```env
IMAP_HOST=imap.mail.yahoo.com
INBOX_EMAIL=your-email@yahoo.com
INBOX_PASSWORD=your-app-password
```

**Google Workspace (Gmail for Business - like mail@quiccle.com):**
```env
IMAP_HOST=imap.gmail.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-app-password
```
*Note: Even for custom domains using Google Workspace, use `imap.gmail.com` as the host*

**Microsoft 365 (Outlook for Business):**
```env
IMAP_HOST=outlook.office365.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-password
```

**Custom IMAP Server:**
```env
IMAP_HOST=mail.quiccle.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-password
```
*Note: Replace `mail.quiccle.com` with your actual mail server hostname*

## 🔍 **How It Works**

1. **Polling**: System polls your inbox every 1 minute (near real-time)
2. **Reading**: Finds unread emails from registered users
3. **Processing**: Extracts reply text, analyzes with LLM
4. **Responding**: Sends automatic response immediately
5. **Using Context**: Next scheduled email incorporates the reply

## 🧪 **Testing**

### Check if Polling is Running

**When backend starts**, look for these log messages:
- `✅ Email reply polling job scheduled (every 1 minute - near real-time)`
- `   IMAP Host: imap.gmail.com`
- `   Inbox Email: your-email@gmail.com`

**If you see warnings instead:**
- `⚠️ Email reply polling DISABLED - Missing environment variables: IMAP_HOST, INBOX_EMAIL, INBOX_PASSWORD`
- This means you need to add these to your `.env` file

**When polling runs** (every 1 minute), you should see:
- `📧 Starting email reply polling - Connecting to imap.gmail.com...`
- `✅ Connected to inbox: your-email@gmail.com`
- `📬 Found X unread message(s) in inbox`
- `📧 EMAIL REPLY RECEIVED from user@example.com`
- `✅ Processed and responded to reply from user@example.com`

### Manual Test (Admin Only)

You can manually trigger polling via API:
```bash
POST /api/admin/test-email-polling
Authorization: Bearer YOUR_ADMIN_SECRET
```

This will immediately poll the inbox and show results in logs.

## ⚠️ **Common Issues**

### Issue 1: "Email reply polling disabled - missing IMAP credentials"
**Solution**: Add `IMAP_HOST`, `INBOX_EMAIL`, and `INBOX_PASSWORD` to `.env`

### Issue 2: "IMAP not available"
**Solution**: Install `imap-tools`: `pip install imap-tools`

### Issue 3: Authentication Failed
**Solution**: 
- For Gmail: Use App Password (not regular password)
- Check IMAP is enabled in email settings
- Verify credentials are correct

### Issue 4: Replies Not Found
**Solution**:
- Check that user's email matches exactly (case-sensitive)
- Verify email is in inbox (not spam/other folders)
- Check that email is unread

## 🔍 **Finding Your IMAP Settings**

### For `mail@quiccle.com`:

**Step 1: Identify Your Email Provider**

Check which email service you're using:

1. **Google Workspace (Gmail for Business)**
   - If you log in at `mail.google.com` or `admin.google.com`
   - IMAP Host: `imap.gmail.com`
   - Port: 993 (SSL)
   - Requires App Password (same as Gmail)

2. **Microsoft 365 / Outlook**
   - If you log in at `outlook.office365.com`
   - IMAP Host: `outlook.office365.com`
   - Port: 993 (SSL)
   - Use your regular password

3. **Custom Email Server**
   - Check with your IT/admin or hosting provider
   - Common hosts: `mail.quiccle.com`, `imap.quiccle.com`, `mail.yourhost.com`
   - Port: Usually 993 (SSL) or 143 (TLS)

**Step 2: Test IMAP Connection**

You can test your IMAP settings using this Python script:

```python
from imap_tools import MailBox

# Test connection
try:
    with MailBox('imap.gmail.com').login('mail@quiccle.com', 'your-password') as mailbox:
        print("✅ Connection successful!")
        print(f"Found {len(list(mailbox.fetch()))} messages")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

**Step 3: Common IMAP Hosts for Custom Domains**

- **Google Workspace**: `imap.gmail.com`
- **Microsoft 365**: `outlook.office365.com`
- **Zoho Mail**: `imap.zoho.com`
- **cPanel/WHM**: Usually `mail.yourdomain.com` or `imap.yourdomain.com`
- **Custom Server**: Check with your hosting provider

## 📋 **Checklist**

- [ ] `imap-tools` installed (`pip install imap-tools`)
- [ ] `beautifulsoup4` installed (`pip install beautifulsoup4`)
- [ ] Identified your email provider (Google Workspace, Microsoft 365, etc.)
- [ ] `IMAP_HOST` set in `.env` (correct host for your provider)
- [ ] `INBOX_EMAIL` set to `mail@quiccle.com` in `.env`
- [ ] `INBOX_PASSWORD` set in `.env` (App Password for Google Workspace)
- [ ] IMAP enabled in email provider settings
- [ ] Tested IMAP connection (optional but recommended)
- [ ] Backend restarted after adding env variables
- [ ] Polling job scheduled (check logs)

## 🚀 **Alternative: Webhook-Based Approach**

If IMAP polling doesn't work for your setup, you could implement:
- **Gmail API** with webhooks (more complex, requires OAuth)
- **SendGrid Inbound Parse** (if using SendGrid)
- **Mailgun Routes** (if using Mailgun)
- **Custom webhook endpoint** for email providers that support it

But IMAP polling is the simplest and works with most email providers.

