import sys
import argparse
import os
from datetime import datetime
from renpho import RenphoClient
from garminconnect import Garmin

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--renpho-email', required=True)
    parser.add_argument('--renpho-password', required=True)
    parser.add_argument('--garmin-email', required=True)
    parser.add_argument('--garmin-password', required=True)
    args = parser.parse_args()

    print("Connecting to Renpho Cloud using renpho-api library...")
    try:
        client = RenphoClient(args.renpho_email, args.renpho_password)
        client.login()
        measurements = client.get_all_measurements()
        
        if not measurements:
            print("Error: Logged in successfully, but found no weight data.")
            sys.exit(1)
            
        weight_info = measurements[0]
        weight_kg = float(weight_info.get("weight"))
        body_fat_pct = float(weight_info.get("bodyfat", weight_info.get("body_fat_percentage", 0)))
        bmi = float(weight_info.get("bmi", 0))
        
        print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")
        
    except Exception as e:
        print(f"Error: Renpho Connection Failed. Reason: {e}")
        sys.exit(1)

    print("Connecting to Garmin Connect...")
    # 👇 FIXED: Point back to the exact hidden folder name the library expects
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    
    target_token_file = os.path.join(token_dir, "garmin.tokens.json")
    if not os.path.exists(target_token_file):
        print(f"Error: Target token file missing at '{target_token_file}'! Make sure you created it on GitHub.")
        sys.exit(1)

    try:
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password
        )
        
        print(f"Authenticating via active repository session tokens at: {token_dir}")
        garmin.login(token_dir)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        garmin.add_body_composition(
            timestamp=today_str,
            weight=weight_kg,
            percent_fat=body_fat_pct,
            bmi=bmi
        )
        print("Success: Stats injected successfully into Garmin Connect!")
        
    except Exception as e:
        print(f"Error: Garmin Connection Failed. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
