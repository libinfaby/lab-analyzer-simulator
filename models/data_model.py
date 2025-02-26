import sqlite3
from datetime import datetime

class DataModel:
    def __init__(self):
        self.db_path = "analyzersim.db"
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables (same as original create_database)
        cursor.execute('''CREATE TABLE IF NOT EXISTS analyzers (...)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS connection_settings (...)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS astm_templates (...)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tests (...)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS samples (...)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS results (...)''')
        
        # Initial data (same as original)
        cursor.execute("SELECT COUNT(*) FROM analyzers")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO analyzers (name) VALUES ('Analyzer 1')")
            cursor.execute("INSERT INTO analyzers (name) VALUES ('Analyzer 2')")
            tests = [('Test_1', 'mmol/l', 0.5, 5.0), ...]
            for test in tests:
                cursor.execute('''INSERT INTO tests (...) VALUES (...)''', (1, *test))
        
        conn.commit()
        conn.close()

    def get_analyzers(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM analyzers")
        analyzers = cursor.fetchall()
        conn.close()
        return analyzers

    def get_connection_settings(self, analyzer_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM connection_settings WHERE analyzer_id = ?", (analyzer_id,))
        settings = cursor.fetchone()
        conn.close()
        return settings

    def get_tests(self, analyzer_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT test_code, unit, lower_range, upper_range FROM tests WHERE analyzer_id = ?", (analyzer_id,))
        tests = cursor.fetchall()
        conn.close()
        return tests

    def save_connection_settings(self, analyzer_id, settings):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Implement save logic similar to original save_connection_settings
        conn.commit()
        conn.close()

    def save_tests(self, analyzer_id, tests):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tests WHERE analyzer_id = ?", (analyzer_id,))
        for test in tests:
            cursor.execute("INSERT INTO tests (analyzer_id, test_code, unit, lower_range, upper_range) VALUES (?, ?, ?, ?, ?)",
                          (analyzer_id, *test))
        conn.commit()
        conn.close()

    def store_samples(self, samples):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for sample in samples:
            cursor.execute("INSERT OR REPLACE INTO samples (sample_number, patient_id, patient_name, date_time) VALUES (?, ?, ?, ?)",
                          (sample["sample_id"], sample["patient_id"], sample["patient_name"], now))
        conn.commit()
        conn.close()

    def generate_results(self, analyzer_id, sample_ids):
        # Implement result generation logic
        pass

    def get_samples(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sample_number, patient_id, patient_name FROM samples ORDER BY date_time DESC")
        samples = cursor.fetchall()
        conn.close()
        return samples

    def get_sample_results(self, sample_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT r.id, t.test_code, r.result_value, t.unit, t.lower_range, t.upper_range, r.sent FROM results r JOIN tests t ON r.test_id = t.id WHERE r.sample_id = ?", (sample_id,))
        results = cursor.fetchall()
        conn.close()
        return results