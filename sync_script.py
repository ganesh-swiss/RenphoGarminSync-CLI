import sys
import argparse
import os
import warnings

# Completely silence the Garth retirement text warnings
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
            
        # 👇 FIXED: Extract the very first entry (index 0) from the list array
        # This gives Python the actual data dictionary it needs to read the metrics!
        weight_info = measurements[0]
        
        # Read the exact metric keys exposed by the community library
        weight_kg = float(weight_info.get("weight"))
        body_fat_pct = float(weight_info.get("bodyfat", weight_info.get("body_fat_percentage", 0)))
        bmi = float(weight_info.get("bmi", 0))
        
        print(f"Latest Renpho Metric: Weight: {weight_kg}kg, Fat: {body_fat_pct}%, BMI: {bmi}")
        
    except Exception as e:
        print(f"Error: Renpho Connection Failed. Reason: {e}")
        sys.exit(1)

    print("Connecting to Garmin Connect...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    os.makedirs(token_dir, exist_ok=True)

    try:
        # Initialize the Garmin engine cleanly
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password
        )
        
        # Inject standard desktop browser profile headers to bypass Cloudflare gates
        browser_user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        
        if hasattr(garmin, 'garth') and hasattr(garmin.garth, 'sess'):
            garmin.garth.sess.headers.update({"User-Agent": browser_user_agent})
        elif hasattr(garmin, 'session') and hasattr(garmin.session, 'headers'):
            garmin.session.headers.update({"User-Agent": browser_user_agent})

        # Process automated local session storage logic
        print(f"Checking for environment-specific cloud tokens at: {token_dir}")
        garmin.login(token_dir)
        
        # Execute health metric injection
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

