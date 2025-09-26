
# Device Health Realtime Dashboard  (Production-ready features)

## Added features
1. **Email (SMTP) + SMS (Twilio placeholder) alert integration**. Configure SMTP and Twilio via environment variables.
2. **Persist history to SQLite** (device_data.db). Each snapshot is stored automatically.
3. **Export CSV** per device via `/export/<device_id>` or Export button in UI.
4. **Dark mode toggle** (persisted in localStorage) + theme variables.
5. **Dockerfile + docker-compose.yml** for easy deployment.

## Environment variables (optional)
- SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO (comma separated)
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO
- DH_DB (path to sqlite file)

## Run locally
1. Create virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python app.py
   ```




