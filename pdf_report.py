import os
import io
import csv
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from monitor import DeviceSimulator
from data_store import DataStore
from alerting import AlertSender
import atexit

# Initialize Flask
app = Flask(__name__, static_folder='static', template_folder='templates')

# DB path
db_path = os.environ.get('DH_DB', 'device_data.db')
store = DataStore(db_path=db_path)
sim = DeviceSimulator(store=store)
alerts = AlertSender(store=store)

settings = {"theme": "light"}  # default theme

# -----------------------
# Routes
# -----------------------

@app.route('/')
def index():
    devices = sim.get_device_list()
    return render_template('index.html', devices=devices)

@app.route('/settings')
def settings_page():
    return render_template('settings.html', settings=settings)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    theme = request.form.get("theme", "light")
    if theme not in ["light", "dark"]:
        theme = "light"
    settings["theme"] = theme
    return redirect(url_for("settings_page"))

@app.route("/export_pdf")
def export_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("📊 Device Health Report", styles['Heading1']))
    elements.append(Spacer(1, 12))

    # Get snapshots
    rows = store.get_recent_snapshots()
    if not rows:
        elements.append(Paragraph("No data available.", styles['Normal']))
    else:
        for r in rows:
            line = f"{r[0]} | {r[1]} | Temp:{r[2]}°C | Mem:{r[3]}% | Volt:{r[4]}V | Status:{r[7]}"
            elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 6))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    filename = f"device_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)

# -----------------------
# Run app
# -----------------------

if __name__ == "__main__":
    try:
        store.init_db()
        sim.start(alert_callback=alerts.check_and_send)
        app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    finally:
        sim.stop()

atexit.register(lambda: sim.stop())
