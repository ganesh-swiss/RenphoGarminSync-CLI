import sys
import argparse
import os
import warnings

# Silence the Garth retirement text warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import datetime

def upload():
    parser = argparse.ArgumentParser()
    parser.add_argument('--garmin-email', required=True)
    parser.add_argument('--garmin-password', required=True)
    parser.add_argument('--weight', required=True, type=float)
    parser.add_argument('--fat', required=True, type=float)
    parser.add_argument('--bmi', required=True, type=float)
    args = parser.parse_args()

    print("Connecting to Garmin Connect via secondary isolated script...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    os.makedirs(token_dir, exist_ok=True)

    try:
        import cloudscraper
        from garminconnect import Garmin
        import garth
        
        # Build advanced desktop browser profile mask
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # 👇 FIXED: Overwrite the correct session instance used by the stable garth module framework
        garth.sess = scraper
        
        # 👇 FIXED: Added is_login_verified=False to prevent the library from checking the token's machine origin
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password,
            is_login_verified=False
        )
        
        print(f"Checking for environment-specific cloud tokens at: {token_dir}")
        garmin.login(token_dir)
        
        # Execute health metric injection
        today_str = datetime.now().strftime("%Y-%m-%d")
        garmin.add_body_composition(
            timestamp=today_str,
            weight=args.weight,
            percent_fat=args.fat,
            bmi=args.bmi
        )
        print("Success: Stats injected successfully into Garmin Connect!")
        
    except Exception as e:
        print(f"Error: Garmin Connection Failed. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload()
