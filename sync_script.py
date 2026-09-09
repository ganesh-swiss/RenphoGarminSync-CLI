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
    https://cloud.renpho.com/api/v3/users/{user_id}/growth_records.json
data_url = f"https://cloud.renpho.com/api/v3/users/{user_id}/growth_records.json"
    data_headers = {"Authorization": f"Bearer {auth_token}", "User-Agent": "Renpho/2.0.0"}
    metrics_resp = requests.get(data_url, headers=data_headers)
    
    latest_record = metrics_resp.json().get("growth_records", [])[0]
    weight_kg = float(latest_record.get("weight"))
    body_fat_pct = float(latest_record.get("body_fat_percentage"))
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
