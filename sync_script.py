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
    login_url = "https://renpho.com"
    payload = {"app_id": "Renpho", "user": {"email": args.renpho_email, "password": args.renpho_password}}
    headers = {"User-Agent": "Renpho/2.0.0 (iPhone; iOS 16.0; Scale)"}
    
    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code != 200:
        print("Error: Renpho Login Failed.")
        sys.exit(1)
        
    # Extract unique tokens from account
    auth_token = response.json().get("terminal_user", {}).get("session_key")
    user_id = response.json().get("terminal_user", {}).get("id")
    
    # Step 2: Fetch scale data using the modern plain-text parameter method
    # 👇 FIXED: Targets modern path & appends the secure user ID right to the URL
    data_url = f"https://renpho.com{user_id}"
    
    # 👇 FIXED: Removed the 'Authorization' token header to bypass encryption triggers
    data_headers = {"User-Agent": "Renpho/2.0.0 (iPhone; iOS 16.0; Scale)"}
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    # Check for a successful server response
    if metrics_resp.status_code != 200:
        print(f"Error: Failed to fetch weight data. Server code: {metrics_resp.status_code}")
        sys.exit(1)
        
    metrics_json = metrics_resp.json()
    
    # Pull data entries out of the modern folder layout
    records = metrics_json.get("body_composition_measurements", [])
    
    if not records:
        print("Error: Successfully connected, but zero weight logs were returned.")
        sys.exit(1)
        
    # Grab the newest entry at the front of the list
    latest_record = records[0]
    
    # Step 3: Extract metric values using standard keys
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_ratio", latest_record.get("body_fat_percentage", 0)))
    bmi = float(latest_record.get("bmi"))
    
    print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")

    # Step 4: Inject data directly into Garmin Connect 
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
