import sys
import argparse
import os
import warnings

# Silences the 'Garth is deprecated' warning text entirely
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
            
        if isinstance(measurements, list):
            weight_info = measurements[0]
        else:
            weight_info = measurements
        
        weight_kg = float(weight_info.get("weight"))
        body_fat_pct = float(weight_info.get("bodyfat", weight_info.get("body_fat_percentage", 0)))
        bmi = float(weight_info.get("bmi", 0))
        
        print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")
        
    except Exception as e:
        print(f"Error: Renpho Connection Failed. Reason: {e}")
        sys.exit(1)

    print("Connecting to Garmin Connect...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    nested_token_file = os.path.join(token_dir, ".garth", "garmin.tokens.json")
    
    if not os.path.exists(nested_token_file):
        print(f"Error: Token file missing at '{nested_token_file}'! Re-check your GitHub folder paths.")
        sys.exit(1)

    try:
        # 👇 FIXED: Changed tokenstore=token_dir to token_dir=token_dir 
        # to match the exact configuration requirements of the stable library build.
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password,
            token_dir=token_dir
        )
        
        # Log in via the local keycard directory to slide past Cloudflare
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
        print(f"Error: Garmin Connection Failed. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
