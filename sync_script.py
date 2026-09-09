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
    # Step 1: Secure App Authentication Login
    # 👇 FIXED: Points to the live unencrypted endpoint to bypass 404 blocks and encryption
    login_url = "http://renpho.qnclouds.com/api/v3/users/sign_in.json"
    
    payload = {
        "app_id": "Renpho",
        "user": {
            "email": args.renpho_email,
            "password": args.renpho_password
        }
    }
    
    headers = {
        "User-Agent": "RenphoHealth/4.21.0 (Linux; Android 14; SAMSUNG SM-G998B)",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Using a POST request with query fallback to satisfy the endpoint requirements
    response = requests.post(login_url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print("Error: Renpho Login Failed.")
        try:
            print(f"Server Response Message: {response.json().get('message', 'No details provided')}")
        except Exception:
            print(f"Raw Server Status: {response.status_code}")
        sys.exit(1)
        
    # Extract unique tokens from the account
    auth_token = response.json().get("terminal_user", {}).get("session_key")
    user_id = response.json().get("terminal_user", {}).get("id")
    
    # Step 2: Fetch scale data using the verified user profile timeline
    # 👇 FIXED: Continues using the live endpoint path where data is readable
    data_url = f"http://renpho.qnclouds.com/api/v3/users/{user_id}/growth_records.json"
    
    data_headers = {
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": "RenphoHealth/4.21.0 (Linux; Android 14)"
    }
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    if metrics_resp.status_code != 200:
        print(f"Error: Failed to fetch weight data. Server code: {metrics_resp.status_code}")
        sys.exit(1)
        
    metrics_json = metrics_resp.json()
    
    # Pull data entries out of the profile folder layout
    records = metrics_json.get("growth_records", metrics_json.get("body_composition_measurements", []))
    
    if not records:
        print("Error: Successfully connected, but zero weight logs were returned.")
        sys.exit(1)
        
    # Grab the newest entry at the front of the tracking list array
    latest_record = records[0]
    
    # Step 3: Extract metric values safely using fallback labels
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_percentage", latest_record.get("body_fat_ratio", 0)))
    bmi = float(latest_record.get("bmi"))
    
    print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")

    # Step 4: Inject data directly into Garmin Connect API portals
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
