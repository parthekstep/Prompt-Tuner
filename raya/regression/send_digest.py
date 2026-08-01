#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send the regression digest via the Gmail API (service account + domain-wide delegation).

Same auth model as the repo's Sheets service account: a Google Workspace service account
whose domain-wide delegation grants the gmail.send scope, impersonating a sender in the
ekstepplus.org domain. No SMTP, no app password.

Env (set as GitHub Actions secrets / repo variables):
  GMAIL_SA_JSON_BASE64  base64 of the service-account JSON (required)
  GMAIL_SENDER          address to send AS / impersonate      (default parth@ekstepplus.org)
  GMAIL_TO              recipient(s), comma-separated          (default parth@ekstepplus.org)
  DIGEST_SUBJECT        subject line                           (default generic)

Reads the HTML body from digest.html (produced by build_digest.py) in the working dir.
"""
import base64, json, os, sys
from email.mime.text import MIMEText

from google.oauth2 import service_account          # google-auth
from googleapiclient.discovery import build         # google-api-python-client

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    sa_b64 = os.environ.get("GMAIL_SA_JSON_BASE64", "")
    if not sa_b64:
        print("GMAIL_SA_JSON_BASE64 not set — skipping Gmail-API send.", file=sys.stderr)
        return 0
    sender = os.environ.get("GMAIL_SENDER", "parth@ekstepplus.org")
    to = os.environ.get("GMAIL_TO", "parth@ekstepplus.org")
    subject = os.environ.get("DIGEST_SUBJECT", "[Prompt Tuner] regression digest")
    html = open("digest.html", encoding="utf-8").read()

    info = json.loads(base64.b64decode(sa_b64))
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES).with_subject(sender)   # impersonate the sender (needs DWD)
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = MIMEText(html, "html", "utf-8")
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent regression digest to {to} (as {sender}).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
