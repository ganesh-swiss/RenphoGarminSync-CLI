import sys
import argparse
from datetime import datetime
import requests
from garminconnect import Garmin

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--renpho-email', required=True)
    parser.add_argument('--renpho-password', required=True)
    parser.add_argument('--garmin-email', required=True)
    parser.add_argument('--garmin-password', required=True)
    args = parser.parse_args()

    print("Connecting to Renpho Cloud...")
    # Authentication header handling
    login_url = "https://cloud.renpho.com/api/v3/users/sign_in.json"
    payload = {"app_id": "Renpho", "user": {"email": args.renpho_email, "password": args.renpho_password}}
    headers = {"User-Agent": "Renpho/2.0.0 (iPhone; iOS 16.0; Scale)"}
    
    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code != 200:
        print("Error: Renpho Login Failed.")
        sys.exit(1)
        
    auth_token = response.json().get("terminal_user", {}).get("session_key")
    user_id = response.json().get("terminal_user", {}).get("id")
    
    # Fetch data timeline
    # 👇 FIX 1: Point to the modern measurements file path
    data_url = f"https://renpho.com"
    data_headers = {"Authorization": f"Bearer {auth_token}", "User-Agent": "Renpho/2.0.0"}
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    # 👇 FIX 2: Safely extract data from the modern folder name
    metrics_json = metrics_resp.json()
    records = metrics_json.get("body_composition_measurements", [])
    
    if not records:
        print("Error: No weight data found in your Renpho Cloud profile.")
        sys.exit(1)
        
    latest_record = records[0]
    
    # 👇 FIX 3: Pull the exact metric labels used by the scale database
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_ratio", latest_record.get("body_fat_percentage", 0)))
    bmi = float(latest_record.get("bmi"))
    
    print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")

    print("Connecting to Garmin Connect...")
    garmin = Garmin(args.garmin_email, args.garmin_password)
    garmin.login()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    garmin.add_body_composition(
        timestamp=today_str,
        weight=weight_kg,
        percent_fat=body_fat_pct,
        bmi=bmi
    )
    print("Success: Stats injected successfully into Garmin Connect!")

if __name__ == "__main__":
    main()
