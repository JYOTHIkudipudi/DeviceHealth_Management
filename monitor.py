import random, threading, time, logging
from datetime import datetime

class DeviceSimulator:
    def __init__(self, store=None):
        self.devices = {
            f"DEV{i}": {"id": f"DEV{i}", "name": f"Device-{i}"} for i in range(1, 6)
        }
        self.running = False
        self.thread = None
        self.store = store
        logging.basicConfig(level=logging.INFO)

    def get_device_list(self):
        return list(self.devices.values())

    def get_device_meta(self, device_id):
        return self.devices.get(device_id)

    def simulate_data(self, device_id):
        temp = random.randint(20, 120)
        mem = random.randint(10, 100)
        volt = round(random.uniform(2.5, 5.5), 2)
        cpu = random.randint(1, 100)
        io = random.randint(1, 100)
        status = "OK"

        if mem > 95:
            status = "Memory Leak Risk"
        if temp > 100:
            status = "Overheating!"
        if volt < 3.0:
            status = "Low Voltage!"

        return {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "device_id": device_id,
            "device_name": self.devices[device_id]["name"],
            "temperature": temp,
            "memory": mem,
            "voltage": volt,
            "cpu": cpu,
            "io": io,
            "status": status,
        }

    def loop(self, alert_callback=None):
        while self.running:
            for device_id in self.devices:
                data = self.simulate_data(device_id)
                if self.store:
                    self.store.insert_snapshot(data)
                if alert_callback:
                    alert_callback(data["device_id"], data["device_name"], data)
            # Use refresh interval from settings if available
            interval = getattr(self.store, 'settings', {}).get("refresh_interval", 2)
            try:
                interval = int(interval)
            except Exception:
                interval = 2
            time.sleep(interval)

    def start(self, alert_callback=None):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.loop, args=(alert_callback,), daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def get_all_status(self):
        return {d: self.simulate_data(d) for d in self.devices}

    def get_device_data(self, device_id):
        return self.simulate_data(device_id)