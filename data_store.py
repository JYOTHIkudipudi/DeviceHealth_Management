import sqlite3

class DataStore:
    def __init__(self, db_path="device_data.db"):
        self.db_path = db_path

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    device_id TEXT,
                    temperature REAL,
                    memory REAL,
                    voltage REAL,
                    cpu REAL,
                    io REAL,
                    status TEXT
                )
            """)
            conn.commit()

    def insert_snapshot(self, data):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO snapshots
                (timestamp, device_id, temperature, memory, voltage, cpu, io, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["timestamp"],
                data["device_id"],
                data["temperature"],
                data["memory"],
                data["voltage"],
                data["cpu"],
                data["io"],
                data["status"]
            ))
            conn.commit()

    def get_history_rows(self, device_id):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT timestamp, temperature, memory, voltage, cpu, io, status
                FROM snapshots
                WHERE device_id=?
                ORDER BY id ASC
            """, (device_id,))
            return c.fetchall()

    def get_recent_snapshots(self, limit=20):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT timestamp, device_id, temperature, memory, voltage, cpu, io, status
                FROM snapshots
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            return c.fetchall()