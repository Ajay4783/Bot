import requests
import pandas as pd
import time
from datetime import datetime
import os
import threading
from flask import Flask

# Flask Website Setup
app = Flask(__name__)

# Unga Variables
api_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
csv_filename = "ar_lottery_live_data.csv" 

# Unga Exact Function
def get_latest_record():
    params = {"pageNo": 1, "pageSize": 1, "ts": int(time.time() * 1000)}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Accept": "application/json"
    }
    try:
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {}).get("list", [])
            if data:
                item = data[0]
                number = int(item.get("number", 0))
                color = item.get("color", "Unknown")
                price = item.get("price", item.get("premium", "N/A")) 

                return {
                    "Period": item.get("issueNumber"),
                    "Number": number,
                    "Big_Small": "Big" if number >= 5 else "Small",
                    "Color": color,
                    "Price": price,
                    "Time_Collected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
    except Exception as e:
        print(f"Error: {e}")
    return None

# Unga Loop Logic (Background Thread-kaga)
def run_bot():
    print("🟢 Advanced Live Bot Started in Background! (Cloud Mode)")
    while True:
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
                print(f"✅ Saved -> Period: {record['Period']} | No: {record['Number']} | {record['Big_Small']} | Color: {record['Color']}")
        
        time.sleep(30)

# Dummy Website Route (Render.com-kaga)
@app.route('/')
def home():
    return "<h1>🟢 AR Lottery Live Bot is Running 24/7!</h1><p>Data is being collected in the background.</p>"

# Cloud Server Start
if __name__ == "__main__":
    # Bot-a background-la start pandrom
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask Web server-a start pandrom
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)