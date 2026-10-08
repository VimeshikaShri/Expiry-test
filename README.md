# Service Expiry Reminder: Python Proof of Concept
​
A lightweight Python script that sends email reminders **21, 14, and 7 days before a service expires**.
​
This project demonstrates an external reminder workflow for a one-time purchase associated with a Chargebee test invoice. The expiry date is entered manually and can be independent of the invoice line item's service period.
​
> **Test use only.** This is not a native Chargebee feature, an official Chargebee integration, or a production-ready notification service.
​
## Features
​
- Three reminder intervals: 21, 14, and 7 days before expiry.
- Dry-run previews by default: emails are sent only with `--send`.
- Simulated dates for testing without waiting several weeks.
- SMTP delivery using STARTTLS.
- Local sent-reminder tracking to reduce duplicate sends.
- A separate record for each purchased service.
- Support for changed expiry dates and inactive services.
- Customer-local dates using an IANA timezone.
- Python standard library only; no third-party Python packages required.
​
## How It Works
​
```text
Chargebee test purchase (optional context)
                  |
                  v
Manually maintained service-expiry record
                  |
                  v
Python script checks whether a reminder is due
                  |
                  v
Dry-run preview OR external SMTP email
                  |
                  v
Successful sends recorded in sent.json
```
​
The script **does not call the Chargebee API**, read a CRM, retrieve invoice service periods, or change any Chargebee data. The invoice ID is a reference included in the email, not a validated link or automation trigger.
​
## Requirements
​
- Python **3.9 or later**.
- IANA timezone data available to Python's `zoneinfo` module. Some systems, particularly Windows, may require `python -m pip install tzdata`.
- An SMTP account that supports **STARTTLS**, typically on port `587`, for actual email delivery.
- An authorized sender address and a test inbox you control.
​
The script does not support implicit TLS on port `465` or OAuth-only SMTP authentication. Confirm your provider's requirements before testing.
​
## Project Files
​
```text
reminders.py     Reminder logic and SMTP sender
services.json    Manually entered service-expiry records
README.md        Documentation
sent.json        Local send history; created after a successful send
```
​
## Quick Start
### 1. Download the project
​
Clone this repository or download and extract it. Open a terminal in the directory containing `reminders.py`.
​
The examples below use `python3`. On Windows, use `py` or `python`, depending on your installation.
​
### 2. Optional: Create a Chargebee test purchase
​
If you want to associate the test with a Chargebee purchase:
​
1. Switch to your Chargebee **Test site**.
2. Create a test customer using an inbox you control.
3. Add a one-time Charge to that customer.
4. Note the resulting invoice ID for the expiry record.
​
Do not use a live customer or live purchase for this proof of concept. Chargebee is not required to run the script.
​
### 3. Configure a service record
​
Edit `services.json`:
​
```json
[
  {
    "service_id": "expiry-test-001",
    "service_name": "Test service access",
    "email": "your-test-inbox@example.com",
    "invoice_id": "test-invoice-id",
    "expiry_date": "2026-10-29",
    "timezone": "Europe/Amsterdam",
    "active": true
  }
]
```
​
| Field | Purpose |
| --- | --- |
| `service_id` | Unique identifier for each purchased service. Must not be duplicated in the file. |
| `service_name` | Service name included in the email. |
| `email` | Recipient address. Use only an inbox you control during testing. |
| `invoice_id` | Optional invoice reference included in the email. |
| `expiry_date` | Authoritative business expiry date in `YYYY-MM-DD` format. |
| `timezone` | IANA timezone used to determine today's date when not simulating. |
| `active` | Set to `false` to skip the service. Defaults to `true` if omitted. |
​
Add separate records for separate purchased services, even if they belong to the same customer.
​
### 4. Preview the reminders
​
For an expiry date of **29 October 2026**, run:
​
```bash
python3 reminders.py --as-of 2026-10-08
python3 reminders.py --as-of 2026-10-15
python3 reminders.py --as-of 2026-10-22
```
​
Expected previews:
​
| Simulated date | Reminder |
| --- | --- |
| 8 October 2026 | 21 days before expiry |
| 15 October 2026 | 14 days before expiry |
| 22 October 2026 | 7 days before expiry |
​
Without `--send`, the script prints **DRY RUN** output. It does not send emails or write send history. Existing send history is still respected.
​
## SMTP Configuration
​
Configure these environment variables in the **same terminal session** used to run the script:
​
| Variable | Value |
| --- | --- |
| `SMTP_HOST` | Provider's SMTP hostname |
| `SMTP_PORT` | STARTTLS port; defaults to `587` if omitted |
| `SMTP_USER` | SMTP login username |
| `SMTP_PASSWORD` | Approved SMTP credential or app password |
| `SMTP_FROM` | Authorized sender address |
​
Your regular mailbox password may not work. Your organization may disable password-based SMTP; consult your provider or IT team.
​
### macOS / Linux
​
```bash
export SMTP_HOST="your-provider-smtp-host"
export SMTP_PORT="587"
export SMTP_USER="your-smtp-username"
export SMTP_FROM="your-authorized-sender@example.com"
```
​
Enter the password with a hidden prompt rather than typing it into a command stored in shell history.
​
**macOS default zsh:**
​
```zsh
read -s "SMTP_PASSWORD?Enter SMTP password: "
echo
export SMTP_PASSWORD
```
​
**Linux / Bash:**
​
```bash
read -s -p "Enter SMTP password: " SMTP_PASSWORD
echo
export SMTP_PASSWORD
```
​
### Windows PowerShell
​
```powershell
$env:SMTP_HOST = "your-provider-smtp-host"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "your-smtp-username"
$env:SMTP_FROM = "your-authorized-sender@example.com"
​
$secret = Read-Host "Enter SMTP password" -AsSecureString
$env:SMTP_PASSWORD = [System.Net.NetworkCredential]::new("", $secret).Password
Remove-Variable secret
```
​
These are temporary session settings, not persistent configuration. The hidden prompt prevents visible password entry; the running script still receives the credential as an environment variable.
​
### Verify configuration without printing secrets
​
```bash
python3 -c "import os; names=['SMTP_HOST','SMTP_PORT','SMTP_USER','SMTP_PASSWORD','SMTP_FROM']; print('\n'.join(n + ': ' + ('SET' if os.environ.get(n) else 'MISSING') for n in names))"
```
​
This checks only whether values exist, not whether they are valid.
​
## Send Test Emails
​
First confirm the recipient in `services.json` is your own test inbox. Then run:
​
```bash
python3 reminders.py --as-of 2026-10-08 --send
python3 reminders.py --as-of 2026-10-15 --send
python3 reminders.py --as-of 2026-10-22 --send
```
​
> These commands send real emails immediately using simulated dates. `--as-of` does not delay delivery.
​
Subjects are prefixed with `[TEST]`. The messages state that no renewal or payment action is required.
​
SMTP acceptance is not proof of inbox delivery. Check your inbox, spam folder, and provider's delivery information.
​
## Test Cases
​
### Duplicate check
​
After successfully sending the 21-day reminder, repeat:
​
```bash
python3 reminders.py --as-of 2026-10-08 --send
```
​
Expected output includes:
​
```text
SKIP already sent
```
​
The tracking key combines the service ID, expiry date, and reminder interval. Keep `sent.json` between runs. Deleting it permits repeat sends.
​
### Expiry extension
​
Change `expiry_date` to `2026-11-05` and preview:
​
```bash
python3 reminders.py --as-of 2026-10-08
python3 reminders.py --as-of 2026-10-15
```
​
The old 8 October reminder should no longer be due. The 15 October preview should show a new 21-day reminder.
​
The script reads the latest JSON each time; it does not queue emails in advance. Changing the expiry creates a different tracking key, so reminders for the new expiry can send even if reminders for the old expiry were already sent.
​
### Inactive service
​
Set `active` to `false` and run on a reminder date. The service should be skipped without sending an email.
​
### No reminder due
​
With the original 29 October expiry, run:
​
```bash
python3 reminders.py --as-of 2026-10-09
```
​
Expected output:
​
```text
No unsent reminders due on this date.
```
​
## Daily Scheduling
​
To check today's date in each record's timezone:
​
```bash
python3 reminders.py --send
```
​
Schedule this command externally once per day using an application scheduler, cron, or Windows Task Scheduler. Make sure that the scheduled process has access to the SMTP environment variables and the same persistent project directory.
​
Do **not** use `--as-of` in a normal scheduled job. Temporary settings from an interactive terminal are not automatically available to scheduled tasks.
​
The script sends only on the exact reminder date. If the daily job is missed, it does not send overdue reminders later.
​
## Troubleshooting
​
| Issue | Check |
| --- | --- |
| Authentication failure | SMTP credentials, app-password requirements, and whether SMTP login is enabled. |
| Connection failure | Hostname, STARTTLS port, network access, and firewall rules. |
| Sender rejected | Whether `SMTP_FROM` is authorized by the provider. |
| `MISSING` configuration | Set variables in the same terminal or scheduled-job environment. |
| `SKIP already sent` | The matching reminder is already in `sent.json`. |
| No reminder due | Simulated/current date, expiry date, timezone, and active status. |
| Timezone not found | Install system timezone data or the `tzdata` package. |
| Email not in inbox | Recipient address, spam folder, and provider delivery status. |
​
## Chargebee Testing Boundaries
​
- Chargebee Time Machine does not advance this script's clock.
- Emails sent by this script do not appear in Chargebee email logs.
- SMTP settings in Chargebee do not configure this script.
- The script does not create Charges, collect payments, renew services, or cancel subscriptions.
- There is no automatic synchronization with Chargebee or a CRM.
​
## Security and Repository Hygiene
​
- Never commit SMTP credentials or real customer data.
- Keep the committed `services.json` limited to fictional example records.
- Prefer a separate local checkout for private testing records.
- Avoid logging credentials or sharing terminal screenshots containing sensitive data.
- Remove session credentials after testing, or close the terminal.
- Use a secrets manager and an approved email provider for a production implementation.
​
Suggested `.gitignore` entries:
​
```gitignore
sent.json
sent.tmp
.env
.venv/
__pycache__/
*.pyc
```
​
The script does not load `.env` files automatically. The `.gitignore` entries do not protect real customer information entered into an already tracked `services.json`; do not commit those edits.
​
## Limitations and Production Considerations
​
This is a **single-process proof of concept**:
​
- Local send history reduces repeat sends but does not guarantee exactly-once delivery. A crash after SMTP acceptance and before saving history can lead to a duplicate.
- Concurrent runs are not supported. Do not run multiple instances at the same time.
- SMTP errors stop the run; there is no automatic retry or failed-message queue.
- Missed reminder dates are not caught up.
- Scheduling is day-based, not a configurable send-time or business-hours workflow.
- Expiry changes, cancellations, recipient preferences, and service eligibility must be maintained manually.
​
Before customer use, add a durable data store, locking, controlled retries, delivery monitoring, secure credential management, recipient-preference handling, and automated updates from the authoritative application or CRM.
​
## References
- [Chargebee Email Notifications](https://www.chargebee.com/docs/billing/2.0/customers/email-notifications-v2)
- [Chargebee Charges](https://www.chargebee.com/docs/billing/2.0/product-catalog/charges)
​
