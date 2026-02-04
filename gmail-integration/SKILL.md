---
name: gmail-integration
description: Read-only Gmail access via IMAP for email analysis, searching, and context gathering. Use when analyzing emails, checking unread messages, searching email history, finding specific senders/topics, or gathering communication context for business intelligence and personal assistance.
---

# Gmail Integration

## Overview

Provides secure read-only access to Gmail via IMAP for email analysis, search, and context gathering. Enables business intelligence, communication tracking, and automated email processing while maintaining security boundaries.

## Quick Start

1. **Setup Gmail access**: See `references/gmail-setup.md` for secure authentication
2. **Basic email check**: `scripts/gmail_reader.py --unread --limit 10`
3. **Search emails**: `scripts/gmail_reader.py --search "BPO partnership"`
4. **Get context**: `scripts/gmail_reader.py --sender broker@example.com --days 7`

## Core Operations

### Check Unread Messages
```bash
scripts/gmail_reader.py --unread [--limit N] [--days N]
```
Returns unread emails with sender, subject, date, and preview text.

### Search Email Content
```bash
scripts/gmail_reader.py --search "keyword OR phrase" [--limit N] [--days N]
```
Full-text search across email subject and body content.

### Filter by Sender
```bash
scripts/gmail_reader.py --sender email@domain.com [--days N]
```
Get recent emails from specific senders (brokers, business contacts, etc).

### Business Intelligence Patterns
Common patterns for business context gathering:

- **BPO Industry**: `--search "BPO OR outsourcing OR partner"`
- **Investment Research**: `--search "earnings OR dividend OR market"`  
- **Meeting Context**: `--search "meeting OR calendar OR agenda"`
- **Opportunities**: `--search "opportunity OR partnership OR deal"`

See `references/email-patterns.md` for detailed examples and analysis templates.

## Resources

### scripts/gmail_reader.py
Main IMAP client for Gmail access with command-line interface. Handles authentication, email retrieval, search, and filtering operations.

### references/gmail-setup.md  
Step-by-step instructions for secure Gmail authentication setup including app passwords, OAuth configuration, and security best practices.

### references/email-patterns.md
Common email analysis patterns, search queries, and templates for extracting business intelligence from email communications.
