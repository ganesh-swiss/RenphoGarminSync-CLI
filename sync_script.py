import sys
import argparse
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
        # Initialize and log into the client
        client = RenphoClient(email=args.renpho_email, password=args.renpho_password)
        client.login()  # Required by the library to fetch internal user IDs
        
        # Grab your modern measurements timeline safely
        weight_info = client.get_latest_measurement()
        
        if not weight_info:
            print("Error: Logged in successfully, but found no recent scale data.")
            sys.exit(1)
            
        # Parse health metrics
        weight_kg = float(weight_info.get("weight"))
        body_fat_pct = float(weight_info.get("body_fat_ratio", weight_info.get("body_fat_percentage", 0)))
        bmi = float(weight_info.get("bmi"))
        
        print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")       
        
    except Exception as e:
        print(f"Error: Renpho Connection Failed. Reason: {e}")
        sys.exit(1)

    # Step 4: Inject data directly into Garmin Connect API portals
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
        print(f"Error: Garmin Connection Failed. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
