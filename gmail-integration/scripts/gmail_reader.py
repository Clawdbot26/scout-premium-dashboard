#!/usr/bin/env python3
"""
Gmail IMAP Reader - Secure read-only Gmail access
Usage: python3 gmail_reader.py [options]
"""

import imaplib
import email
import json
import argparse
import sys
from datetime import datetime, timedelta
from email.header import decode_header
import re
import os

class GmailReader:
    def __init__(self, email_addr=None, password=None):
        """Initialize Gmail IMAP connection"""
        self.email_addr = email_addr or os.getenv('GMAIL_USER')
        self.password = password or os.getenv('GMAIL_APP_PASSWORD')
        self.imap = None
        
        if not self.email_addr or not self.password:
            raise ValueError("Gmail credentials required. Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables")
    
    def connect(self):
        """Establish IMAP connection to Gmail"""
        try:
            self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
            self.imap.login(self.email_addr, self.password)
            self.imap.select('INBOX')
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def decode_header_value(self, value):
        """Decode email header values"""
        if value:
            decoded = decode_header(value)[0]
            if decoded[1]:
                return decoded[0].decode(decoded[1])
            return decoded[0]
        return ""
    
    def clean_body(self, body):
        """Clean email body text"""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', body)
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean)
        # Truncate to reasonable preview length
        return clean.strip()[:300] + "..." if len(clean) > 300 else clean.strip()
    
    def get_emails(self, search_criteria="ALL", limit=10, days=None):
        """Retrieve emails based on search criteria"""
        if not self.connect():
            return []
        
        try:
            # Add date filter if specified
            if days:
                since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
                search_criteria = f'SINCE {since_date} {search_criteria}'
            
            status, messages = self.imap.search(None, search_criteria)
            email_ids = messages[0].split()[-limit:]  # Get most recent emails
            
            emails = []
            for email_id in reversed(email_ids):  # Most recent first
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                subject = self.decode_header_value(msg['subject'])
                sender = self.decode_header_value(msg['from'])
                date = msg['date']
                
                # Get email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                emails.append({
                    'id': email_id.decode(),
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body_preview': self.clean_body(body)
                })
            
            return emails
            
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []
        finally:
            if self.imap:
                self.imap.close()
                self.imap.logout()
    
    def get_unread(self, limit=10, days=None):
        """Get unread emails"""
        return self.get_emails("UNSEEN", limit, days)
    
    def search_emails(self, query, limit=10, days=None):
        """Search emails by content"""
        # Gmail IMAP search syntax
        search_query = f'TEXT "{query}"'
        return self.get_emails(search_query, limit, days)
    
    def get_from_sender(self, sender_email, limit=10, days=None):
        """Get emails from specific sender"""
        search_query = f'FROM "{sender_email}"'
        return self.get_emails(search_query, limit, days)

def main():
    parser = argparse.ArgumentParser(description='Gmail IMAP Reader')
    parser.add_argument('--unread', action='store_true', help='Get unread emails')
    parser.add_argument('--search', type=str, help='Search email content')
    parser.add_argument('--sender', type=str, help='Get emails from specific sender')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of results')
    parser.add_argument('--days', type=int, help='Limit to emails from last N days')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    try:
        reader = GmailReader()
        
        # Determine which operation to perform
        if args.unread:
            emails = reader.get_unread(args.limit, args.days)
        elif args.search:
            emails = reader.search_emails(args.search, args.limit, args.days)
        elif args.sender:
            emails = reader.get_from_sender(args.sender, args.limit, args.days)
        else:
            emails = reader.get_emails("ALL", args.limit, args.days)
        
        # Output results
        if args.json:
            print(json.dumps(emails, indent=2))
        else:
            if not emails:
                print("No emails found")
                return
            
            print(f"\nFound {len(emails)} emails:\n")
            for i, email in enumerate(emails, 1):
                print(f"{i}. FROM: {email['sender']}")
                print(f"   SUBJECT: {email['subject']}")
                print(f"   DATE: {email['date']}")
                print(f"   PREVIEW: {email['body_preview']}")
                print("-" * 80)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()