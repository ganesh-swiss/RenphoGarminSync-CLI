import sys
import argparse
import hashlib
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

    print("Connecting to Renpho Legacy Cloud...")
    # Hash the password to match legacy security protocols
    hashed_password = hashlib.md5(args.renpho_password.encode('utf-8')).hexdigest()
    
    login_url = "https://cloud.renpho.com"
    payload = {"user": {"email": args.renpho_email, "password": hashed_password}}
    headers = {"User-Agent": "QingNiu/4.3.0 (iPhone; iOS 15.0; Scale)"}
    
    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code != 200:
        print("Error: Legacy Renpho Login Failed. Verify your email/password matches your phone app.")
        sys.exit(1)
        
    auth_token = response.json().get("terminal_user", {}).get("session_key")
    user_id = response.json().get("terminal_user", {}).get("id")
    
    # Fetch data history records from legacy cluster
    data_url = f"https://cloud.renpho.com{user_id}/growth_records.json?per_page=1"
    data_headers = {"Authorization": f"Bearer {auth_token}", "User-Agent": "QingNiu/4.3.0"}
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    records = metrics_resp.json().get("growth_records", [])
    if not records:
        print("Error: No weight records found on your Renpho account.")
        sys.exit(1)
        
    latest_record = records[0]
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_percentage"))
    bmi = float(latest_record.get("bmi"))
    
    print(f"Latest Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")

    print("Connecting to Garmin Connect...")
    try:
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
    except Exception as e:
        print(f"Garmin error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
