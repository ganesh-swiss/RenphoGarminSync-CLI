import sys
import argparse
import os
import json
from datetime import datetime
from renpho import RenphoClient
from garminconnect import Garmin

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--renpho-email', required=True)
    parser.add_argument('--renpho-password', required=True)
    parser.add_argument('--garmin-email', required=True)
    parser.add_argument('--garmin-password', required=True)
    # 👇 NEW: Accepts the text token right from GitHub secrets
    parser.add_argument('--garmin-tokens', required=False, default="")
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
    # Define a clean directory for temporary token storage inside the cloud runner
    token_dir = os.path.join(os.getcwd(), "g_tokens")
    os.makedirs(token_dir, exist_ok=True)
    
    # 👇 NEW: If a token secret is provided, write it directly to the session file
    if args.garmin_tokens:
        print("Pre-loading Garmin session token keycard from GitHub Secrets...")
        try:
            # Recreate the file Garmin expects using your text secret
            with open(os.path.join(token_dir, "session.json"), "w") as f:
                f.write(args.garmin_tokens)
        except Exception as token_err:
            print(f"Warning: Could not write token file: {token_err}")

    try:
        garmin = Garmin(args.garmin_email, args.garmin_password)
        
        # Load the pre-authorized session folder
        print(f"Authenticating via active session folder...")
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
