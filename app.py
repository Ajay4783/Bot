import requests
import pandas as pd
import time
from datetime import datetime
import os
import threading
from flask import Flask, send_file

app = Flask(__name__)
csv_filename = "ar_lottery_live_data.csv" 

def get_latest_record():
    params = {"pageNo": 1, "pageSize": 1, "ts": int(time.time() * 1000)}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://draw.ar-lottery01.com/",
        "Origin": "https://draw.ar-lottery01.com",
        "Connection": "keep-alive"
    }
    try:
        # Timeout add pannirukkom
        response = requests.get("https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json", params=params, headers=headers, timeout=10)
        
        # API status check (Cloud-la IP block aagirukkaa nu paarkka)
        print(f"📡 API Status Code: {response.status_code}", flush=True) 
        
        if response.status_code == 200:
            data = response.json().get("data", {}).get("list", [])
            if data:
                item = data[0]
                number = int(item.get("number", 0))
                return {
                    "Period": item.get("issueNumber"),
                    "Number": number,
                    "Big_Small": "Big" if number >= 5 else "Small",
                    "Color": item.get("color", "Unknown"),
                    "Price": item.get("price", item.get("premium", "N/A")),
                    "Time_Collected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
    except Exception as e:
        print(f"❌ API Error: {e}", flush=True)
    return None

def run_bot():
    print("🟢 Advanced Live Bot Started in Background! (Cloud Mode)", flush=True)
    
    # Error thavirkka, app start aana udaneye oru empty CSV file create pannidrom
    if not os.path.exists(csv_filename):
        pd.DataFrame(columns=["Period", "Number", "Big_Small", "Color", "Price", "Time_Collected"]).to_csv(csv_filename, index=False)
        print("📁 Empty CSV File Created Successfully!", flush=True)

    while True:
        print("⏳ Fetching new data...", flush=True)
        record = get_latest_record()
        
        if record:
            file_exists = os.path.isfile(csv_filename)
            is_new = True
            
            if file_exists:
                df_existing = pd.read_csv(csv_filename).tail(10)
                if str(record["Period"]) in df_existing["Period"].astype(str).values:
                    is_new = False
            
            if is_new:
                df = pd.DataFrame([record])
                df.to_csv(csv_filename, mode='a', header=not file_exists, index=False)
                print(f"✅ Saved -> Period: {record['Period']} | No: {record['Number']} | {record['Big_Small']}", flush=True)
            else:
                print(f"⚠️ Old Period, waiting for next... ({record['Period']})", flush=True)
        else:
            print("❌ Failed to get data from API.", flush=True)
        
        time.sleep(30)

# Render Cloud-kaga Thread-a veliye start pandrom
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

@app.route('/')
def home():
    return "<h1>🟢 AR Lottery Live Bot is Running 24/7!</h1><p>Data is being collected in the background.</p><h3><a href='/download'>Click here to Download CSV Data</a></h3>"

@app.route('/download')
def download_data():
    try:
        return send_file(csv_filename, as_attachment=True)
    except Exception as e:
        return f"Innum data file create aagala! Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)