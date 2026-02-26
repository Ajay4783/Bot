import requests
import pandas as pd
import time
from datetime import datetime
import os
import threading
from flask import Flask, send_file

app = Flask(__name__)
csv_filename = "ar_lottery_live_data.csv" 

# !!! INGA UNGA SCRAPERAPI KEY-A PODUNGA !!!
SCRAPER_API_KEY = "1ec6c00053c004944e854b7712defbb9"

def get_latest_record():
    target_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
    
    # ScraperAPI vazhiya request-a anuppurom
    proxy_url = f"https://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}"
    
    try:
        # Proxy vazhiya porathala timeout konjam athigama vekkalaam (20s)
        response = requests.get(proxy_url, timeout=20)
        
        print(f"📡 Proxy Status: {response.status_code}", flush=True) 
        
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
        print(f"❌ Proxy/API Error: {e}", flush=True)
    return None

def run_bot():
    print("🟢 Bot with Proxy Started!", flush=True)
    if not os.path.exists(csv_filename):
        pd.DataFrame(columns=["Period", "Number", "Big_Small", "Color", "Price", "Time_Collected"]).to_csv(csv_filename, index=False)

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
                print(f"✅ Saved Period: {record['Period']}", flush=True)
            else:
                print(f"⚠️ Already exists: {record['Period']}", flush=True)
        else:
            print("❌ Proxy-layum block aagirukku pola!", flush=True)
        
        # Free credits save panna interval-a 60 seconds (1 min)-ah mathikkonga
        time.sleep(60) 

# Render setup...
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

@app.route('/')
def home():
    return "<h1>🟢 Bot with Proxy is Running!</h1>"

@app.route('/download')
def download_data():
    return send_file(csv_filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)