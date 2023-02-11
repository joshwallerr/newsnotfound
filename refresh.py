# CRON set to run script every 45mins - 1hour

import csv
import datetime

def remove_old_rows(filename):
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    twelve_hours_ago = (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime("%H:%M:%S")

    updated_rows = [row for row in rows if row["time"] >= twelve_hours_ago or row["time"] <= current_time]

    with open(filename, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["headline", "time"])
        writer.writeheader()
        writer.writerows(updated_rows)

if __name__ == "__main__":
    remove_old_rows("covered.csv")