import argparse
import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

#main things
API_URL = ("https://services3.arcgis.com/J7ZFXmR8rSmQ3FGf/arcgis/rest/services/"
           "gauges_2_view/FeatureServer/0/query")
PAGE_SIZE = 1000                            #records per request
MAX_ATTEMPTS = 3                            #retry a failed request up to three times
SL_OFFSET = timedelta(hours=5, minutes=30)  #UTC Sri Lanka time
DROP_COLS = ["globalid", "Creator", "EditDate", "Editor"]


#download the file 
def get_page(params):
    """Request one page from the API, retrying up to MAX_ATTEMPTS times."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=60)
            response.raise_for_status()               #HTTP error like 500
            data = response.json()
            if "error" in data:                        #Arcgis report the error in json
                raise RuntimeError(f"API error: {data['error']}")
            return data
        except Exception as err:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS} failed: {err}")
            if attempt == MAX_ATTEMPTS:
                raise                                  #give up the main log error
            time.sleep(10 * attempt)                   #wait 10s n then 20s


def fetch_all():
    """Download every record, page by page."""
    params = {
        "where": "1=1",                 #all rec
        "outFields": "*",               #+all colm
        "f": "json",
        "orderByFields": "OBJECTID ASC",  #fixing th order 
        "resultOffset": 0,
        "resultRecordCount": PAGE_SIZE,
    }
    rows = []
    while True:
        data = get_page(params)
        features = data.get("features", [])
        rows.extend(f["attributes"] for f in features)
        if features and data.get("exceededTransferLimit"):
            params["resultOffset"] += PAGE_SIZE      #more pages left
        else:
            break
    return pd.DataFrame(rows)


#clean the data
def clean(df):
    """Rename the time column, drop system columns, convert to Sri Lanka time."""
    df = df.rename(columns={"CreationDate": "Observation_Time"})
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    for col in df.columns:
        if "time" in col.lower() or "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], unit="ms") + SL_OFFSET
            except (ValueError, TypeError):
                pass
    return df


#saving as each station
def save_by_station(df, out_dir):
    """Add new readings to one CSV per station. Returns rows added."""
    os.makedirs(out_dir, exist_ok=True)
    added = 0
    for station in df["gauge"].dropna().unique():
        new = df[df["gauge"] == station]
        safe = str(station).replace("/", "_").replace("\\", "_").replace(" ", "_")
        path = os.path.join(out_dir, f"{safe}.csv")

        if os.path.exists(path):
            old = pd.read_csv(path)
            old["Observation_Time"] = pd.to_datetime(old["Observation_Time"])
            before = len(old)
            combined = pd.concat([old, new])
        else:
            before = 0
            combined = new

        combined = (combined.drop_duplicates(subset=["Observation_Time"], keep="last")
                            .sort_values("Observation_Time"))
        combined.to_csv(path, index=False)
        added += len(combined) - before
    return added


#write the log 
def write_log(log_path, status, fetched=0, stations=0, added=0, error=""):
    """Append one line about this run to the run log."""
    folder = os.path.dirname(log_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    new_file = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["run_time_utc", "status", "records_fetched",
                             "stations", "rows_added", "error"])
        writer.writerow([datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                         status, fetched, stations, added, error])


#main fucntion to run 
def main():
    parser = argparse.ArgumentParser(description="C1 hourly gauge collector")
    parser.add_argument("--out", default="Station_Rainfall_CSVs",
                        help="folder for the per-station CSV files")
    parser.add_argument("--log", default="run_log.csv",
                        help="CSV file that records every run")
    args = parser.parse_args()

    try:
        df = fetch_all()
        if df.empty:
            write_log(args.log, "no_data")
            print("No records returned.")
            return
        df = clean(df)
        if "gauge" not in df.columns:
            raise RuntimeError("column 'gauge' not found in the data")
        added = save_by_station(df, args.out)
        stations = df["gauge"].nunique()
        write_log(args.log, "ok", len(df), stations, added)
        print(f"Fetched {len(df)} records from {stations} stations, added {added} new rows.")
    except Exception as err:
        write_log(args.log, "failed", error=str(err)[:300])
        print(f"Run failed: {err}")
        sys.exit(1)   #the exit cron 


if __name__ == "__main__":
    main()