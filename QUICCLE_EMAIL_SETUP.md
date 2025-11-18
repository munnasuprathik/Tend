# Quick Setup for mail@quiccle.com

## 🎯 **Quick Configuration**

Add these to your `.env` file:

```env
# For Google Workspace (if quiccle.com uses Gmail)
IMAP_HOST=imap.gmail.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-app-password-here
```

OR

```env
# For Microsoft 365 / Outlook
IMAP_HOST=outlook.office365.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-password-here
```

OR

```env
# For Custom Email Server
IMAP_HOST=mail.quiccle.com
INBOX_EMAIL=mail@quiccle.com
INBOX_PASSWORD=your-password-here
```

## 🔍 **How to Find Which One to Use**

### Option 1: Check Your Email Login Page

1. **If you log in at `mail.google.com` or `admin.google.com`**:
   - Use: `IMAP_HOST=imap.gmail.com`
   - You'll need an **App Password** (see below)

2. **If you log in at `outlook.office365.com`**:
   - Use: `IMAP_HOST=outlook.office365.com`
   - Use your regular password

3. **If you log in at a custom URL** (like `mail.quiccle.com` or your hosting provider):
   - Use: `IMAP_HOST=mail.quiccle.com` (or whatever your mail server is)
   - Use your regular password

### Option 2: Check Email Client Settings

If you use Outlook, Thunderbird, or Apple Mail:
1. Open your email client settings
2. Look for "Incoming Mail Server" or "IMAP Server"
3. That's your `IMAP_HOST`

### Option 3: Ask Your IT/Admin

Contact whoever manages your email and ask:
- "What is the IMAP server hostname for mail@quiccle.com?"
- "What port does IMAP use?" (usually 993)

## 🔑 **Getting an App Password (Google Workspace Only)**

If you're using Google Workspace:

1. Go to: https://myaccount.google.com/apppasswords
   - (Or: Google Account → Security → 2-Step Verification → App Passwords)

2. Select:
   - App: "Mail"
   - Device: "Other (Custom name)"
   - Name: "InboxInspire"

3. Click "Generate"

4. Copy the 16-character password (no spaces)

5. Use this password in `INBOX_PASSWORD` (NOT your regular password)

## ✅ **After Setup**

1. Save the `.env` file
2. Restart your backend server
3. Check logs for: `✅ Email reply polling job scheduled (every 1 minute - near real-time)`
4. Test by sending a reply to `mail@quiccle.com` - it should be processed within 1 minute!

## 🧪 **Test Connection**

You can test if your settings work:

```bash
# In Python
python -c "from imap_tools import MailBox; MailBox('YOUR_IMAP_HOST').login('mail@quiccle.com', 'YOUR_PASSWORD'); print('✅ Success!')"
```

Replace `YOUR_IMAP_HOST` and `YOUR_PASSWORD` with your actual values.

## ❓ **Still Not Working?**

1. **Check if IMAP is enabled** in your email provider settings
2. **Verify the email address** matches exactly (case-sensitive)
3. **Check firewall/network** - IMAP port 993 must be accessible
4. **Try the test endpoint**: `POST /api/admin/test-email-polling` (admin only)
5. **Check backend logs** for specific error messages

