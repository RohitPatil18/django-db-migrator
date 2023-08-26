import csv
import os

from django.conf import settings
from django.db import connections

DATASET = {}

BACKUP_DIR = os.path.join(settings.BASE_DIR, "backups")


class DatabaseExportService:
    def __init__(self, tablename):
        self.tablename = tablename

        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def get_columns(self, cursor):
        columns = [desc.name for desc in cursor.description]
        return columns

    def fetch_data(self, cursor):
        cursor.execute("SELECT * FROM {0}".format(self.tablename))
        table_data = cursor.fetchall()
        return table_data

    def save_to_csv(self, data, columns):
        filename = f"{self.tablename}.csv"
        filepath = os.path.join(BACKUP_DIR, filename)
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  # Write column names
            writer.writerows(data)

    def export(self):
        conn = connections["source"]
        cursor = conn.cursor()

        data = self.fetch_data(cursor)
        columns = self.get_columns(cursor)

        self.save_to_csv(data, columns)

        cursor.close()
        conn.close()
