import sys
import argparse
import os
import warnings

# Completely silence the Garth retirement text warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import datetime
from renpho import RenphoClient

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
    os.makedirs(token_dir, exist_ok=True)

    try:
        # 👇 FIXED: Inject cloudscraper to bypass Cloudflare signatures completely!
        import cloudscraper
        from garminconnect import Garmin
        import garth
        
        # Build an advanced desktop browser profile mask
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Overwrite the global network connection session with our Cloudflare-proof scraper
        garth.client.sess = scraper
        
        # Initialize the clean engine securely under the network mask
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password
        )
        
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
