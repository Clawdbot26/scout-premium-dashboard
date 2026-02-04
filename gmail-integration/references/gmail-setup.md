# Gmail Setup Guide

## Secure Read-Only Access Configuration

This guide shows how to set up secure, read-only Gmail access using app-specific passwords and IMAP.

## Method 1: App-Specific Password (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", enable **2-Step Verification** if not already enabled
3. Follow the setup wizard to configure your phone/authenticator

### Step 2: Generate App Password
1. Still in Google Account Security, click **2-Step Verification**
2. Scroll down to **App passwords** section
3. Click **App passwords** (may need to re-authenticate)
4. Select app: **Mail**
5. Select device: **Other (Custom name)**
6. Enter name: `OpenClaw-ReadOnly`
7. Click **Generate**
8. **Copy the 16-character password** - you can't view it again

### Step 3: Configure Environment Variables

**Option A: Terminal Session (Temporary)**
```bash
export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-app-password"
```

**Option B: Shell Profile (Persistent)**
Add to your `~/.zshrc` or `~/.bashrc`:
```bash
export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-app-password"
```
Then run: `source ~/.zshrc`

**Option C: OpenClaw Config (Most Secure)**
Store credentials in OpenClaw's secure auth system:
```bash
openclaw auth add gmail --provider custom \
  --env GMAIL_USER="your.email@gmail.com" \
  --env GMAIL_APP_PASSWORD="your-16-char-app-password"
```

### Step 4: Test Connection
```bash
python3 gmail-integration/scripts/gmail_reader.py --unread --limit 5
```

## Method 2: OAuth2 (Advanced)

For production environments or shared systems, OAuth2 provides more granular permissions:

### Prerequisites
- Google Cloud Console project
- Gmail API enabled
- OAuth2 credentials configured

### Setup Process
1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth2 credentials (Desktop application)
4. Download credentials JSON file
5. Install required packages: `pip3 install google-auth google-auth-oauthlib google-api-python-client`

**Note**: OAuth2 implementation available on request for enterprise deployments.

## Security Best Practices

### Access Scope
- **Read-only**: IMAP access cannot send emails or modify folders
- **App password**: Limited to IMAP/POP access only
- **Revocable**: Can be disabled anytime in Google Account settings

### Data Handling
- Email content is processed locally only
- No data is stored or transmitted externally
- Credentials stored in secure environment variables
- Connection uses encrypted IMAP SSL

### Monitoring Access
- Check [Google Account Activity](https://myaccount.google.com/security) for access logs
- App passwords show usage in security dashboard
- Revoke access anytime: Account Settings > Security > App passwords

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Verify 2FA is enabled
- Check app password is correct (16 characters, no spaces)
- Ensure IMAP is enabled in Gmail settings

**"Connection timeout"**
- Check network/firewall settings
- Gmail IMAP server: `imap.gmail.com:993`
- Ensure SSL/TLS is enabled

**"No emails returned"**
- Check search criteria syntax
- Verify mailbox has content in specified date range
- Try basic `--unread` test first

### Gmail IMAP Settings
If you see authentication errors, verify IMAP is enabled:
1. Gmail > Settings (gear icon) > See all settings
2. Forwarding and POP/IMAP tab
3. IMAP Access: **Enable IMAP**
4. Save changes

## Integration Examples

### Daily Brief Integration
```bash
# Morning unread check
gmail_reader.py --unread --days 1 --limit 20

# BPO industry intelligence
gmail_reader.py --search "BPO OR outsourcing OR partnership" --days 7

# Investment updates
gmail_reader.py --search "earnings OR dividend OR market" --days 3
```

### Business Intelligence Patterns
```bash
# Partner communications
gmail_reader.py --search "partner OR partnership OR collaboration"

# Meeting preparation
gmail_reader.py --search "meeting OR agenda OR calendar" --days 2

# Opportunity tracking
gmail_reader.py --search "opportunity OR proposal OR deal"
```