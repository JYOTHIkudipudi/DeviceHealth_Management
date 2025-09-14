import os
import smtplib
from email.message import EmailMessage

class AlertSender:
    def __init__(self, store=None):
        self.store = store
        self.smtp_host = os.environ.get('SMTP_HOST')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_pass = os.environ.get('SMTP_PASS')
        self.alert_email_to = os.environ.get('ALERT_EMAIL_TO')

    def check_and_send(self, device_id, device_name, snapshot):
        subject = f"[ALERT] {device_name} ({device_id}) - {snapshot.get('status')}"
        body = f"""Device: {device_name} ({device_id})
Time: {snapshot.get('timestamp')}
Temp: {snapshot.get('temperature')} °C
Memory: {snapshot.get('memory')} %
Voltage: {snapshot.get('voltage')} V
CPU: {snapshot.get('cpu')} %
I/O: {snapshot.get('io')} %
Status: {snapshot.get('status')}
"""
        if self.smtp_host and self.smtp_user and self.smtp_pass and self.alert_email_to:
            try:
                self._send_email(subject, body)
                print("✅ Alert email sent")
            except Exception as e:
                print("❌ Email send failed:", e)
        else:
            print("⚠️ SMTP not configured; skipping email. Alert details below:")
            print(subject)
            print(body)
        # Twilio SMS integration placeholder
        # TODO: Add SMS sending logic if necessary

    def _send_email(self, subject, body):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = [x.strip() for x in (self.alert_email_to or "").split(',') if x.strip()]
        msg.set_content(body)
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as s:
            s.starttls()
            s.login(self.smtp_user, self.smtp_pass)
            s.send_message(msg)