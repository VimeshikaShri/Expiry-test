#!/usr/bin/env python3
"""Manual-expiry reminder proof of concept. Standard library only; Python 3.9+."""
import argparse
import json
import os
import smtplib
import ssl
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--as-of', help='Simulate YYYY-MM-DD (test use only)')
p.add_argument('--send', action='store_true', help='Actually send via SMTP; default is dry run')
a = p.parse_args()
records = json.loads((BASE / 'services.json').read_text())
state_path = BASE / 'sent.json'
sent = json.loads(state_path.read_text()) if state_path.exists() else []
if not isinstance(records, list) or not isinstance(sent, list):
    raise ValueError('Records and state must be JSON arrays')
ids = [r['service_id'] for r in records]
if len(ids) != len(set(ids)):
    raise ValueError('service_id must be unique per purchased service')
count = 0
for r in records:
    if not r.get('active', True):
        print('SKIP inactive:', r['service_id'])
        continue
    expiry = date.fromisoformat(r['expiry_date'])
    today = date.fromisoformat(a.as_of) if a.as_of else datetime.now(ZoneInfo(r['timezone'])).date()
    for days in (21, 14, 7):
        due = expiry - timedelta(days=days)
        if today != due:
            continue
        key = '|'.join((r['service_id'], r['expiry_date'], str(days)))
        if key in sent:
            print('SKIP already sent:', key)
            continue
        count += 1
        subject = f"[TEST] {r['service_name']} ends in {days} days"
        body = (f"Hello,\n\nYour {r['service_name']} is scheduled to end on {expiry}.\n"
                f"This is a TEST {days}-day reminder for service {r['service_id']}.\n"
                f"Chargebee invoice reference: {r.get('invoice_id', 'not supplied')}.\n\n"
                "No renewal or payment action is required for this test.\n")
        if not a.send:
            print(f'DRY RUN | {due} | To: {r["email"]} | {subject}\n{body}')
            continue
        host = os.environ['SMTP_HOST']
        port = int(os.environ.get('SMTP_PORT', '587'))
        sender = os.environ['SMTP_FROM']
        user = os.environ['SMTP_USER']
        password = os.environ['SMTP_PASSWORD']
        msg = EmailMessage()
        msg['From'], msg['To'], msg['Subject'] = sender, r['email'], subject
        msg.set_content(body)
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
        sent.append(key)
        temp = state_path.with_suffix('.tmp')
        temp.write_text(json.dumps(sent, indent=2))
        temp.replace(state_path)
        print('SENT:', key)
if count == 0:
    print('No unsent reminders due on this date.')
