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
    # Step 1: Handle secure app login token authentication
    login_url = "https://cloud.renpho.com/api/v3/users/sign_in.json"
    payload = {"app_id": "Renpho", "user": {"email": args.renpho_email, "password": args.renpho_password}}
    headers = {"User-Agent": "Renpho/2.0.0 (iPhone; iOS 16.0; Scale)"}
    
    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code != 200:
        print("Error: Renpho Login Failed.")
        sys.exit(1)
        
    auth_token = response.json().get("terminal_user", {}).get("session_key")
    user_id = response.json().get("terminal_user", {}).get("id")
    
    # Step 2: Fetch data timeline via unencrypted legacy server channel
    # 👇 FIXED: Corrected domain spelling, added 'renpho.', and fixed missing slash!
    base_domain = "http://" + "renpho" + "." + "qnclouds" + ".com"
    data_url = f"{base_domain}/api/v3/users/{user_id}/growth_records.json"
    
    data_headers = {"Authorization": f"Bearer {auth_token}", "User-Agent": "Renpho/2.0.0"}
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    # Check for a successful server connection before decoding JSON arrays
    if metrics_resp.status_code != 200:
        print(f"Error: Failed to fetch weight data. Server code: {metrics_resp.status_code}")
        sys.exit(1)
        
    metrics_json = metrics_resp.json()
    
    # Verify and parse both old and new data timeline container folders safely
    records = metrics_json.get("growth_records", metrics_json.get("body_composition_measurements", []))
    
    if not records:
        print("Error: Successfully connected, but zero weight logs were returned.")
        sys.exit(1)
        
    latest_record = records[0]
    
    # Pull individual scale weights and verify types
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_percentage", latest_record.get("body_fat_ratio", 0)))
    bmi = float(latest_record.get("bmi"))
    
    print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")

    # Step 3: Inject the payload directly into Garmin Connect API portals
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
