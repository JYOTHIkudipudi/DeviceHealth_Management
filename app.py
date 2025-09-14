import os
import io
import csv
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for
from monitor import DeviceSimulator
from data_store import DataStore
from alerting import AlertSender
from reportlab.pdfgen import canvas
import atexit

app = Flask(__name__, static_folder='static', template_folder='templates')

# DB path
db_path = os.environ.get('DH_DB', 'device_data.db')
store = DataStore(db_path=db_path)
sim = DeviceSimulator(store=store)
alerts = AlertSender(store=store)

settings = {
    "theme": "light",
    "alert_email": "",
    "refresh_interval": 2,
}

@app.route('/')
def index():
    devices = sim.get_device_list()
    return render_template('index.html', devices=devices, settings=settings)

@app.route('/device/<device_id>')
def device_page(device_id):
    device = sim.get_device_meta(device_id)
    if not device:
        return "Device not found", 404
    return render_template('device.html', device=device, devices=sim.get_device_list())

@app.route('/api/devices')
def api_devices():
    return jsonify(sim.get_all_status())

@app.route('/api/device/<device_id>')
def api_device(device_id):
    return jsonify(sim.get_device_data(device_id))

@app.route('/settings')
def settings_page():
    return render_template('settings.html', settings=settings)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    theme = request.form.get("theme", "light")
    if theme not in ["light", "dark"]:
        theme = "light"
    settings["theme"] = theme

    alert_email = request.form.get("alert_email", "")
    if alert_email:
        settings["alert_email"] = alert_email

    refresh_interval = request.form.get("refresh_interval", "2")
    try:
        refresh_interval = int(refresh_interval)
    except ValueError:
        refresh_interval = 2
    settings["refresh_interval"] = refresh_interval

    return redirect(url_for("index"))

# Export CSV for one device
@app.route('/export/<device_id>')
def export_device_csv(device_id):
    rows = store.get_history_rows(device_id)
    if not rows:
        return "No data", 404

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'temperature', 'memory', 'voltage', 'cpu', 'io', 'status'])
    for r in rows:
        cw.writerow(r)
    mem = io.BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)

    filename = f"{device_id}_history_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

# Export all data CSV
@app.route('/export_csv')
def export_all_csv():
    conn = sqlite3.connect(store.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, device_id, temperature, memory, voltage, cpu, io, status FROM snapshots ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No data", 404

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'device_id', 'temperature', 'memory', 'voltage', 'cpu', 'io', 'status'])
    cw.writerows(rows)
    mem = io.BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)

    filename = f"all_devices_history_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

# Export PDF (daily summary)
@app.route("/export_pdf")
def export_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, "Device Health Report")
    c.setFont("Helvetica", 10)

    rows = store.get_recent_snapshots()
    y = 770
    for r in rows:
        line = f"{r[0]} | {r[1]} | Temp:{r[2]}C | Mem:{r[3]}% | Volt:{r[4]}V | Status:{r[7]}"
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = 770

    c.save()
    buffer.seek(0)
    filename = f"device_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)

# ---- MAIN ----
if __name__ == '__main__':
    store.init_db()
    # only start simulator if not reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        sim.start(alert_callback=alerts.check_and_send)
        atexit.register(sim.stop)

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))